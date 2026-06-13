from db import get_parameter_range

def get_rag_status(readings, age, sex):
    results = {}
    for name, value in readings.items():
        range_data = get_parameter_range(name, sex, age)
        if range_data is None:
            continue  # no hardcoded range for this parameter, skip it

        ref_min, ref_max, amber_low, amber_high = range_data

        if ref_min <= value <= ref_max:
            status = 'Green'
        elif (amber_low <= value < ref_min) or (ref_max < value <= amber_high):
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