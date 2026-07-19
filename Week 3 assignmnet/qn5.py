trips = [
    {"distance": 1.5, "hour": 14},
    {"distance": 5.0, "hour": 22},
    {"distance": 12.0, "hour": 3},
    {"distance": 8.5, "hour": 10},
    {"distance": 2.0, "hour": 23}
]
for trip in trips:
    distance = trip["distance"]
    hour = trip["hour"]

    if distance <= 2:
        fare = 150

    elif distance <= 10:
        fare = 150 + ((distance - 2) * 35)

    else:
        fare = 150 + (8 * 35) + ((distance - 10) * 28)

    if hour >= 22 or hour <= 5:
        fare = fare + (fare * 10 / 100)

    print(f"Distance: {distance} km, Hour: {hour}")
    print(f"Fare: NPR {fare:.2f}\n")