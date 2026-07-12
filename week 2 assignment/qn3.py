permit_fee = float(input("Enter permit fee per person: "))
guide_fee = float(input("Enter guide fee: "))
number_of_trekkers = int(input("Enter number of trekkers: "))

total_cost = (permit_fee * number_of_trekkers) + guide_fee
cost_per_person = total_cost / number_of_trekkers

print("\n----- Trekking Cost -----")
print(f"Total Cost: NPR {total_cost:.2f}")
print(f"Cost Per Person: NPR {cost_per_person:.2f}")