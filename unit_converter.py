import math


# ----------------------------------------------------
# Length conversion (base: meter)
# ----------------------------------------------------
LENGTH = {
    "m": 1,
    "km": 1000,
    "cm": 0.01,
    "mm": 0.001,
    "ft": 0.3048,
    "in": 0.0254,
    "mile": 1609.34,
}


# ----------------------------------------------------
# Mass conversion (base: kilogram)
# ----------------------------------------------------
MASS = {
    "kg": 1,
    "g": 0.001,
    "mg": 0.000001,
    "lb": 0.453592,
    "ton": 1000,
}


# ----------------------------------------------------
# Speed conversion (base: m/s)
# ----------------------------------------------------
SPEED = {
    "m/s": 1,
    "km/h": 0.277778,
    "mph": 0.44704,
    "knot": 0.514444,
}


# ----------------------------------------------------
# Pressure conversion (base: Pascal)
# ----------------------------------------------------
PRESSURE = {
    "pa": 1,
    "kpa": 1000,
    "bar": 100000,
    "psi": 6894.76,
}


# ----------------------------------------------------
# Energy conversion (base: Joule)
# ----------------------------------------------------
ENERGY = {
    "j": 1,
    "kj": 1000,
    "cal": 4.184,
    "kwh": 3.6e6,
}


# ----------------------------------------------------
# Power conversion (base: Watt)
# ----------------------------------------------------
POWER = {
    "w": 1,
    "kw": 1000,
    "hp": 745.7,
}


# ----------------------------------------------------
# Area conversion (base: square meter)
# ----------------------------------------------------
AREA = {
    "m2": 1,
    "cm2": 0.0001,
    "mm2": 0.000001,
    "km2": 1e6,
    "ft2": 0.092903,
}


# ----------------------------------------------------
# Volume conversion (base: cubic meter)
# ----------------------------------------------------
VOLUME = {
    "m3": 1,
    "cm3": 1e-6,
    "mm3": 1e-9,
    "l": 0.001,
    "ml": 0.000001,
}


# ----------------------------------------------------
# Temperature conversion
# ----------------------------------------------------
def convert_temperature(value, from_unit, to_unit):
    if from_unit == "c":
        if to_unit == "f":
            return value * 9 / 5 + 32
        if to_unit == "k":
            return value + 273.15
        return value

    if from_unit == "f":
        if to_unit == "c":
            return (value - 32) * 5 / 9
        if to_unit == "k":
            return (value - 32) * 5 / 9 + 273.15
        return value

    if from_unit == "k":
        if to_unit == "c":
            return value - 273.15
        if to_unit == "f":
            return (value - 273.15) * 9 / 5 + 32
        return value

    return None


# ----------------------------------------------------
# General conversion formatter
# ----------------------------------------------------
def convert(value, from_unit, to_unit):
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()

    # temperature has unique formulas
    if from_unit in ["c", "f", "k"] and to_unit in ["c", "f", "k"]:
        return convert_temperature(value, from_unit, to_unit)

    # determine the correct category
    categories = [LENGTH, MASS, SPEED, PRESSURE, ENERGY, POWER, AREA, VOLUME]
    names = ["length", "mass", "speed", "pressure", "energy", "power", "area", "volume"]

    for cat, name in zip(categories, names):
        if from_unit in cat and to_unit in cat:
            base = value * cat[from_unit]
            return base / cat[to_unit]

    return None


# ----------------------------------------------------
# Format telegram output
# ----------------------------------------------------
def convert_pretty(input_value, from_unit, to_unit):
    try:
        v = float(input_value)
    except:
        return "Value must be a number."

    result = convert(v, from_unit, to_unit)

    if result is None:
        return "Units not compatible or not recognized."

    return f"{v} {from_unit} = {result} {to_unit}"
