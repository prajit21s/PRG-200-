import math

station_name = "Kathmandu Weather Station"

temperatures = [18.4, 22.1, 15.7, 29.3, 11.8, 25.6, 19.2]


def get_average(temps):
    total = sum(temps)
    average = total / len(temps)
    return average


def get_deviation(temps):
    mean = get_average(temps)

    total = 0

    for temp in temps:
        total += (temp - mean) ** 2

    variance = total / len(temps)
    deviation = math.sqrt(variance)

    return deviation


def get_summary(temps):
    average = get_average(temps)
    deviation = get_deviation(temps)

    print(station_name)
    print("----------------------------")
    print(f"Minimum temperature: {min(temps)}°C")
    print(f"Maximum temperature: {max(temps)}°C")
    print(f"Average temperature: {average:.2f}°C")
    print(f"Standard deviation: {deviation:.2f}°C")


get_summary(temperatures)

# mean is a local variable inside get_deviation().
# print(mean) outside the function would cause a NameError.