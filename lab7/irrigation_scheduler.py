import math


def parse_zone(text):
    """
    Parses a zone string formatted as '<name>:<area>'.
    Hardened against None, non-strings, missing delimiters, and invalid numeric values.
    Returns (name: str, area: float) if valid, or None if invalid.
    """
    if not isinstance(text, str):
        return None
    text = text.strip()
    if not text or ':' not in text:
        return None
    parts = text.split(':')
    if len(parts) != 2:
        return None
    name = parts[0].strip().title()
    if not name:
        return None
    try:
        area = float(parts[1].strip())
        if math.isnan(area) or math.isinf(area) or area <= 0:
            return None
        return name, area
    except (ValueError, TypeError):
        return None


def moisture_average(readings_csv):
    """
    Calculates integer average moisture from a comma-separated list of readings.
    Hardened against None, non-strings, empty values, and non-integers.
    Returns integer average if valid, or None if invalid / empty.
    """
    if not isinstance(readings_csv, str):
        return None
    readings_csv = readings_csv.strip()
    if not readings_csv:
        return None
    parts = readings_csv.split(',')
    values = []
    for r in parts:
        r_str = r.strip()
        if not r_str:
            return None
        try:
            val = int(r_str)
            if val < 0:
                return None
            values.append(val)
        except (ValueError, TypeError):
            return None
    if not values:
        return None
    return sum(values) // len(values)


def water_needed(text):
    """
    Computes water requirement from string formatted as '<plot_area>|<rainfall>'.
    Hardened against None, non-strings, missing delimiters, and invalid numbers.
    Returns water needed (float) if valid, or None if invalid.
    """
    if not isinstance(text, str):
        return None
    text = text.strip()
    if not text or '|' not in text:
        return None
    parts = text.split('|')
    if len(parts) != 2:
        return None
    try:
        plot = float(parts[0].strip())
        rain = float(parts[1].strip())
        if math.isnan(plot) or math.isinf(plot) or math.isnan(rain) or math.isinf(rain):
            return None
        if plot < 0 or rain < 0:
            return None
        need = plot * 5.0 - rain
        return max(need, 0.0)
    except (ValueError, TypeError):
        return None


def main():
    print("==== Running parse_zone ====")
    user_input = input("Enter zone:area in m2 (e.g. north:120): ")
    result = parse_zone(user_input)
    print("Zone and Area:", result)

    print("\n==== Running moisture_average ====")
    user_input = input("Enter moisture readings as CSV (e.g. 40,35,50): ")
    result = moisture_average(user_input)
    print("Average Moisture:", result)

    print("\n==== Running water_needed ====")
    user_input = input("Enter area|rainfall (e.g. 120|8): ")
    result = water_needed(user_input)
    print("Water Needed:", result)


if __name__ == "__main__":
    main()