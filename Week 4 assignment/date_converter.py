bs_months = [
    "Baisakh", "Jestha", "Ashadh", "Shrawan",
    "Bhadra", "Ashwin", "Kartik", "Mangsir",
    "Poush", "Magh", "Falgun", "Chaitra"
]

customers = [
    {"name": "Ramesh Thapa", "date": "1985-06-24", "cal": "AD", "need": "BS", "style": "full"},
    {"name": "Sunita Karki", "date": "2055-09-10", "cal": "BS", "need": "AD", "style": "iso"},
    {"name": "Bikash Rai", "date": "1998-11-30", "cal": "AD", "need": "BS", "style": "nepali"},
    {"name": "Anjali Gurung", "date": "2040-01-05", "cal": "BS", "need": "AD", "style": "full"}
]

def convert_date(date_str, from_cal, to_cal):

    year, month, day = date_str.split("-")

    year = int(year)

    if from_cal == to_cal:
        return date_str

    elif from_cal == "AD" and to_cal == "BS":
        year += 56

    elif from_cal == "BS" and to_cal == "AD":
        year -= 56

    return f"{year}-{month}-{day}"

for customer in customers:
    
    converted = convert_date(
        customer["date"],
        customer["cal"],
        customer["need"]
    )

    print(
        f"{customer['name']} | Original: "
        f"{customer['date']} {customer['cal']} | "
        f"Converted: {converted} {customer['need']}"
    )