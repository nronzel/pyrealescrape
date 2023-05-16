import re


def split_lot_size(text):
    match = re.match(r"([\d.,]+)([^\d]+)", text)
    if match:
        size = float(match.group(1).replace(",", ""))
        unit = match.group(2).strip()
        if "acre" in unit:
            size *= 43560  # convert acres to square feet
        return size, unit
    else:
        return None, None


def house_to_yard(lotsize, sqft):
    return round(int(lotsize) / int(sqft), 2)
