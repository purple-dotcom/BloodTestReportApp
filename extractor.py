import pdfplumber
import re
import pytesseract
from datetime import datetime

def check_n_extract(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text_pages = []
        for page in pdf.pages:
            text = page.extract_text()
            if text and text.strip():
                text_pages.append(text)

        if text_pages:
            return '\n'.join(text_pages)

        scanned_pages = []
        for page in pdf.pages:
            image_text = pytesseract.image_to_string(page.to_image().original)
            if image_text and image_text.strip():
                scanned_pages.append(image_text)

        if scanned_pages:
            return '\n'.join(scanned_pages)

        return "unknown"
    
def parse_text(text):
    text = re.sub(r'(\d),(\d)', r'\1\2', text)
    patient_info = {}
    report_readings = {}

    # --- patient info patterns ---

    age_match        = re.search(r"Age\s*:\s*(\d+)", text)
    sex_match        = re.search(r"Sex\s*:\s*(Male|Female)", text, re.IGNORECASE)
    gender_match     = re.search(r"Gender\s*:\s*(Male|Female)", text, re.IGNORECASE)
    age_gender_match  = re.search(r"(\d+)\s*/\s*(Male|Female)", text, re.IGNORECASE)
    age_gender_match2 = re.search(r"(\d+)\s*Years?\s*/\s*(Male|Female)", text, re.IGNORECASE)
    age_sex_match = re.search(r"(\d+)\s*YRS?\s*/\s*(M|F)\b", text, re.IGNORECASE)
    name_match  = re.search(r"^([A-Z][a-z]+(?:\s[A-Z]\.?\s?[A-Za-z]+)*)\s+Sample Collected", text, re.MULTILINE)
    name_match2 = re.search(r"Name\s*:\s*([A-Za-z\s\.]+?)(?:\s{2,}|$)", text, re.MULTILINE)
    name_match3 = re.search(r"Patient\s*Name\s*:\s*(?:Mr\.?|Mrs\.?|Ms\.?|Dr\.?)?\s*([A-Z][A-Z\s]+?)(?=\s+(?:Age|Gender|Sex|Ref|DOB|Date|Contact|Phone)|\s{2,}|$)", text, re.MULTILINE | re.IGNORECASE)
    name_match4 = re.search(r"^(Mr\.?|Mrs\.?|Ms\.?|Dr\.?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)", text, re.MULTILINE)
    lab_match = re.search(r"^(?!.*@)(.+?(?:Laboratory|Lab|Pathology|Diagnostics)[^\n]*)", text, re.MULTILINE | re.IGNORECASE)
    date_match  = re.search(r"(\d{1,2}[\s\-\/]\w+[\s\-\/]\d{2,4})", text)

    # age — age_gender_match2 is more specific ("52 Years / Male") so check it first
    if age_match:
        patient_info["age"] = int(age_match.group(1))
    elif age_gender_match2:
        patient_info["age"] = int(age_gender_match2.group(1))
    elif age_gender_match:
        patient_info["age"] = int(age_gender_match.group(1))
    elif age_sex_match:
        patient_info["age"] = int(age_sex_match.group(1))

    if sex_match:
        patient_info["sex"] = sex_match.group(1).capitalize()
    elif gender_match:
        patient_info["sex"] = gender_match.group(1).capitalize()
    elif age_gender_match2:
        patient_info["sex"] = age_gender_match2.group(2).capitalize()
    elif age_gender_match:
        patient_info["sex"] = age_gender_match.group(2).capitalize()
    elif age_sex_match:
        patient_info["sex"] = 'Male' if age_sex_match.group(2).upper() == 'M' else 'Female'

    if name_match:
        patient_info["name"] = name_match.group(1)
    elif name_match3:
        patient_info["name"] = name_match3.group(1).strip().title()
    elif name_match2:
        patient_info["name"] = name_match2.group(1).strip()
    elif name_match4:
        patient_info["name"] = name_match4.group(2).strip()  # group(2) skips the title

    if lab_match:
        patient_info["lab_name"] = lab_match.group(1).strip()
    else:
        patient_info["lab_name"] = "Unknown Lab"

    if date_match:
        raw_date = date_match.group(1)
        for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d %b %Y", "%d %B %Y"):
            try:
                patient_info["report_date"] = datetime.strptime(raw_date, fmt).strftime("%Y-%m-%d")
                break
            except ValueError:
                continue
        else:
            patient_info["report_date"] = None
    else:
        patient_info["report_date"] = None

    param_pattern = re.compile(
        r"^(.+?)[ \t]+(\d+\.?\d*)[ \t]+"
        r"[^\d\n]+?"                              # unit + label — everything non-digit non-newline
        r"(\d+\.?\d*)[ \t]*-[ \t]*(\d+\.?\d*)",  # ref range
        re.MULTILINE
    )

    multiline_param_pattern = re.compile(
        r"^([A-Za-z][A-Za-z0-9 ()\/%\-]*?)\s*\n"  # name line (starts with letter)
        r"(?:[A-Za-z][^\n]*\n)?"                    # optional noise line (starts with letter)
        r"[ \t]*(\d+\.?\d*)[ \t]+"                  # measured value
        r"\S+[ \t]+"                                 # unit
        r"(?:[A-Za-z][^\n:]*:\s*)?"                 # optional label e.g. "Adult Male :"
        r"(\d+\.?\d*)\s*-\s*(\d+\.?\d*)",           # ref range: min - max
        re.MULTILINE
    )

    # stuff to skip
    skip_patterns = [
        r"^Calculated$",
        r"^Primary Sample",
        r"^Investigation",
        r"^Generated",
        r"^Sample Collection",
        r"^Thanks",
        r"^Instruments",
        r"^Interpretation",
    ]
    skip_regex = re.compile("|".join(skip_patterns), re.MULTILINE)

    for match in param_pattern.finditer(text):
        name    = match.group(1).strip()
        name = re.sub(r'[\s,_=]+$', '', name) 
        name = re.sub(r'\s+[A-Z]$', '', name)
        value   = float(match.group(2))

        if skip_regex.match(name):
            continue
        report_readings[name] = value

    for match in multiline_param_pattern.finditer(text):
        name    = match.group(1).strip()
        name = re.sub(r'[\s,_=]+$', '', name)
        name = re.sub(r'\s+[A-Z]$', '', name)
        value   = float(match.group(2))

        if skip_regex.match(name):
            continue
        if name in report_readings:   # already captured by single line pattern
            continue
        report_readings[name] = value

    below_pattern = re.compile(r"^(.+?)[ \t]+(\d+\.?\d*)[ \t]+\S+[ \t]+[Bb]elow[ \t]+(\d+\.?\d*)", re.MULTILINE)
    upper_bound_pattern = re.compile(r"^(.+?)[ \t]+(\d+\.?\d*)[ \t]+\S+[ \t]+<[ \t]*(\d+\.?\d*)", re.MULTILINE)
    
    for match in below_pattern.finditer(text):
        name    = match.group(1).strip()
        name = re.sub(r'[\s,_=]+$', '', name)
        name = re.sub(r'\s+[A-Z]$', '', name)
        value   = float(match.group(2))

        if skip_regex.match(name):
            continue
        if name in report_readings:
            continue
        report_readings[name] = value

    for match in upper_bound_pattern.finditer(text):
        name = match.group(1).strip()
        name = re.sub(r'[\s,_=]+$', '', name)
        name = re.sub(r'\s+[A-Z]$', '', name)
        value = float(match.group(2))

        if skip_regex.match(name):
            continue
        if name in report_readings:
            continue
        report_readings[name] = value

    return patient_info, report_readings

name_aliases = {
    'hemoglobin': 'Hemoglobin',
    'haemoglobin': 'Hemoglobin',
    'hgb': 'Hemoglobin',
    'hb': 'Hemoglobin',
    'total leukocyte count': 'WBC',
    'tlc': 'WBC',
    'tlc (total leucocyte count)': 'WBC',
    'wbc': 'WBC',
    'neutrophils': 'Neutrophils',
    'neutrophil': 'Neutrophils',
    'lymphocytes': 'Lymphocytes',
    'lymphocyte': 'Lymphocytes',
    'monocytes': 'Monocytes',
    'monocyte': 'Monocytes',
    'eosinophils': 'Eosinophils',
    'eosinophil': 'Eosinophils',
    'basophils': 'Basophils',
    'basophil': 'Basophils',
    'platelet count': 'Platelets',
    'plt': 'Platelets',
    'total rbc count': 'RBC',
    'rbc': 'RBC',
    'hematocrit value, hct': 'HCT',
    'hematocrit value': 'HCT',
    'hct': 'HCT',
    'pcv': 'HCT',
    'mean corpuscular volume, mcv': 'MCV',
    'mean corpuscular volume': 'MCV',
    'mcv': 'MCV',
    'mean cell haemoglobin, mch': 'MCH',
    'mean cell haemoglobin': 'MCH',
    'mch': 'MCH',
    'mean cell haemoglobin con, mchc': 'MCHC',
    'mean cell haemoglobin con': 'MCHC',
    'mchc': 'MCHC',
    'pdw': 'PDW',
    'mpv': 'MPV',
    'rdw-cv': 'RDW-CV',
    'rdw': 'RDW-CV',
    'glucose fasting (plasma)': 'Glucose Fasting',
    'glucose fasting': 'Glucose Fasting',
    'fasting blood glucose': 'Glucose Fasting',
    'glucose random': 'Glucose Random',
    'glucose pp (plasma)': 'Glucose PP',
    'glucose pp': 'Glucose PP',
    'hba1c': 'HbA1c',
    'glycosylated haemoglobin': 'HbA1c',
    'average blood glucose (abg)': 'Average Blood Glucose',
    'average blood glucose': 'Average Blood Glucose',
    'total bilirubin': 'Total Bilirubin',
    'conjugated bilirubin': 'Conjugated Bilirubin',
    'unconjugated bilirubin(indirect)': 'Unconjugated Bilirubin',
    'unconjugated bilirubin': 'Unconjugated Bilirubin',
    'total protein': 'Total Protein',
    'albumin, serum': 'Albumin',
    'albumin': 'Albumin',
}

def normalize_readings(readings):
    normalized = {}
    for name, value in readings.items():
        canonical = name_aliases.get(name.strip().lower(), name.strip())
        normalized[canonical] = value
    return normalized