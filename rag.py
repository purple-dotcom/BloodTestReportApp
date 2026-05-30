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