previous = float(input("Enter previous meter reading: "))
current = float(input("Enter current meter reading: "))
rate = float(input("Enter rate per unit: "))
service_charge = float(input("Enter service charge: "))

units = current - previous
bill = (units * rate) + service_charge

print("\n----- Electricity Bill -----")
print(f"Units Consumed: {units:.2f}")
print(f"Total Bill: NPR {bill:.2f}")