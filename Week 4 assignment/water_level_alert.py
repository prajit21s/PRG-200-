sensors = [
    ("Chatara", 2.8),
    ("Tribeni Ghat", 5.4),
    ("Koshi Barrage", 4.1),
    ("Sunsari Bridge", 1.9),
    ("Saptakoshi Camp", 6.0)
]

def check_water_level(location, level_metres):

    if level_metres < 3:
        return "Safe"

    elif level_metres <= 5:
        return "Warning - Alert nearby villages"

    else:
        return "DANGER - Evacuate immediately!"

for location, level in sensors:
    status = check_water_level(location, level)
    print(f"{location} ({level} m): {status}")