import pdfplumber
import re
import pytesseract

def check_n_extract(pdf_path):
    text_found, image_found = False, False
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages[:4]:
            text = page.extract_text()
            if text and text.strip():
                text_found = True
            if page.images:
                image_found = True
    
        if text_found:  #ignore decorative images
            return pdf.pages[0].extract_text()
        elif image_found:  # no text at all, actual scanned pdf
            image = pdf.pages[0].to_image().original
            return pytesseract.image_to_string(image)
        else:
            return "unknown"

# loc1 = r"C:\Users\DELL\Downloads\proton-recovery-kit.pdf"
# print(check_n_extract(loc1))
# loc2 = r"C:\Users\DELL\Downloads\CBC-test-report-format-example-sample-template-Drlogy-lab-report.pdf"
# txt = check_n_extract(loc2)

# for line in txt.split('\n'):
#     if any(x in line for x in ['MCH', 'MCHC', 'RDW']):
#         print(repr(line))

def parse_text(text):
    patient_info = {}
    report_readings = {}

    # patient info patterns
    age_match = re.search(r"Age\s*:\s*(\d+)", text)
    sex_match = re.search(r"Sex\s*:\s*(\w+)", text)
    name_match = re.search(r"^([A-Z][a-z]+(?:\s[A-Z]\.?\s?[A-Za-z]+)*)\s+Sample Collected", text, re.MULTILINE)

    if age_match:
        patient_info["age"] = int(age_match.group(1))
    if sex_match:
        patient_info["sex"] = sex_match.group(1)
    if name_match:
        patient_info["name"] = name_match.group(1)

    # parameter pattern
    param_pattern = re.compile(
    r"^(.+?)\s+(\d+\.?\d*)\s+(?:Low|High|Borderline|Calculated)?\s*(\d+\.?\d*)\s*-\s*(\d+\.?\d*)\s+(\S+)",
    re.MULTILINE
    )

    # noise to skip
    skip_patterns = [
        r"^[A-Z][A-Z\s]{4,}$",  # all caps AND at least 5 chars long
        r"^Calculated$",
        r"^Primary Sample",
        r"^Investigation",
        r"^Generated",
        r"^Sample Collection",
        r"^Thanks",
        r"^Instruments",
        r"^Interpretation"
    ]
    skip_regex = re.compile("|".join(skip_patterns), re.MULTILINE)

    for match in param_pattern.finditer(text):
        name = match.group(1).strip()
        value = float(match.group(2))
        unit = match.group(5)

        # skip if name matches noise
        if skip_regex.match(name):
            continue
        report_readings[name] = value

    return patient_info, report_readings

# readings = parse_text(txt) #returns 2 dictionaries
# print(output)

fallback = {
    "Total RBC count": "RBC",
    "Total WBC count": "WBC",
    "Neutrophils": "NEUT",
    "Lymphocytes": "LYMPH",
    "Eosinophils": "EOS",
    "Monocytes": "MONO",
    "Basophils": "BASO",
    "Platelet Count": "PLT"
}

def get_short_name_values(readings):
    cleaned = {}
    for name, value in readings.items():
        match = re.search(r"\((\w+)\)", name)
        if match:
            short = match.group(1)
        elif name in fallback:
            short = fallback[name]
        else:
            short = name
        cleaned[short] = value
    return cleaned

#print(get_short_name_values(readings[1])) #pass the 2nd dictionary (report_readings)