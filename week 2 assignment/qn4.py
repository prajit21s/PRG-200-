monthly_salary = float(input("Enter monthly salary: "))
bonus_percent = float(input("Enter bonus percentage: "))

bonus = (bonus_percent / 100) * monthly_salary
total_salary = monthly_salary + bonus

print("\n----- Dashain Bonus -----")
print(f"Bonus Amount: NPR {bonus:.2f}")
print(f"Total Salary with Bonus: NPR {total_salary:.2f}")