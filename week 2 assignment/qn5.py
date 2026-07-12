weight = float(input("Enter weight in kg: "))
height = float(input("Enter height in meters: "))

bmi = weight / (height ** 2)

print("\n----- BMI Report -----")
print(f"BMI: {bmi:.2f}")