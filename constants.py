def list_constants():
    return {
        "General Mechanical": {
            "Acceleration due to gravity g": "9.81 m/s²",
            "Gas constant R": "8.314 J/mol·K",
            "Atmospheric pressure": "101325 Pa",
            "Standard temperature": "273.15 K",
        },

        "Aerospace": {
            "Speed of sound at sea level": "343 m/s",
            "Air density at sea level": "1.225 kg/m³",
            "Lift equation constant (0.5 rho v²)": "Used in lift and drag equations",
            "Earth radius": "6371 km",
        },

        "Automobile": {
            "Fuel energy density petrol": "46.4 MJ/kg",
            "Diesel energy density": "45.5 MJ/kg",
            "Air fuel ratio gasoline": "14.7:1",
            "Rolling resistance coefficient": "0.01 to 0.015",
        },

        "Marine": {
            "Density of seawater": "1025 kg/m³",
            "Ocean pressure increase": "1 atm per 10 meters depth",
            "Drag coefficient for ship hulls": "0.1 to 0.2",
            "Average wave speed": "5 to 15 m/s",
        },

        "Electrical": {
            "Speed of electricity": "≈ 200,000 km/s",
            "Electron charge": "1.602 × 10⁻¹⁹ C",
            "Permittivity of free space": "8.85 × 10⁻¹² F/m",
            "Permeability of free space": "4π × 10⁻⁷ H/m",
        }
    }

CONSTANTS = {
    "Speed of Light": "3.0 × 10^8 m/s"
}

def constants_pretty():
    data = list_constants()
    output = "Engineering Constants\n\n"

    for category, items in data.items():
        output += f"{category}:\n"
        for name, value in items.items():
            output += f"- {name}: {value}\n"
        output += "\n"

    return output.strip()
