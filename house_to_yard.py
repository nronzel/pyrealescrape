import re


def parse_lot_size(text):
    # match groups of digits possibly separated by comma or period, and any non-digit characters
    match = re.match(r"([\d.,]+)([^\d]+)", text)
    if match:
        size = float(match.group(1).replace(",", ""))
        unit = match.group(2).strip()
        if "acre" in unit:
            size *= 43560  # convert acres to square feet
        return int(size)
    else:
        return None


def split_lot_size(text):
    match = re.match(r"([\d.,]+)([^\d]+)", text)
    if match:
        size = match.group(1)
        unit = match.group(2).strip()
        return size, unit
    else:
        return None, None


def house_to_yard(lotsize, sqft):
    return round(int(lotsize) / int(sqft), 2)
