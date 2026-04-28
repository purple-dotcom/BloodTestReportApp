import re
from extractor import check_n_extract, parse_text, get_short_name_values

ranges = {
    "Hb":  {"male": (13.0, 17.0), "female": (12.0, 16.0)},
    "RBC": {"male": (4.5, 5.5),   "female": (3.8, 4.8)},
    "PCV" : {"male": (40, 50), "female": (36, 46)},
    "MCV": {"male": (83, 101), "female": (83, 101)},
    "MCH": {"male": (27, 32), "female": (27, 32)},
    "MCHC": {"male": (32.5, 34.5), "female": (32.5, 34.5)},
    "RDW": {"male": (11.6, 14), "female": (11.6, 14)},
    "WBC": {"male": (4000, 11000), "female": (4000, 11000)},
    "NEUT": {"male": (50, 62), "female": (50, 62)},
    "LYMPH": {"male": (20, 40), "female": (20, 40)},
    "EOS": {"male": (0, 6), "female": (0, 6)},
    "MONO": {"male": (0, 10), "female": (0, 10)},
    "BASO": {"male": (0, 2), "female": (0, 2)},
    "PLT": {"male": (150000, 410000), "female": (150000, 410000)}
    }

def get_rag_status(readings, sex):
    results = {}
    sex = sex.lower()

    for short_name, value in readings.items():
        if short_name not in ranges:
            continue

        ref_min, ref_max = ranges[short_name][sex]
        range_ = ref_max - ref_min
        buffer = range_ * 0.05

        if ref_min <= value <= ref_max:
            status = "Green"
        elif (ref_min - buffer) <= value < ref_min or ref_max < value <= (ref_max + buffer):
            status = "Amber"
        else:
            status = "Red"

        results[short_name] = {'value' : value, 'status' : status}
    
    return results

loc = r"C:\Users\DELL\Downloads\CBC-test-report-format-example-sample-template-Drlogy-lab-report.pdf"
text = check_n_extract(loc)
patient_info, raw_readings = parse_text(text)
cleaned_readings = get_short_name_values(raw_readings)

print(get_rag_status(cleaned_readings, patient_info["sex"]))