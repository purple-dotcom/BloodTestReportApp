# from extractor import check_n_extract, parse_text
def get_rag_status(report_readings):
    results = {}
    for name, (value, ref_min, ref_max) in report_readings.items():
        buffer = 0.05 * (ref_max - ref_min)

        if ref_min <= value <= ref_max:
            status = 'Green'
        elif (ref_min - buffer) <= value < ref_min or ref_max < value <= (ref_max + buffer):
            status = 'Amber'
        else:
            status = 'Red'

        results[name] = {
            'value':   value,
            'ref_min': ref_min,
            'ref_max': ref_max,
            'status':  status
        }
    return results

# loc = r"C:\Users\ayaan\Downloads\IRFAN SHAIKH_1777724991000.pdf"
# print(get_rag_status(parse_text(check_n_extract(loc))[1]))