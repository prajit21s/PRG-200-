purchase = float(input("Enter total purchase amount: "))
member = input("Are you a loyalty member? (yes/no): ")

if purchase < 1000:
    discount = 0
elif purchase < 5000:
    discount = 5
elif purchase < 15000:
    discount = 10
else:
    discount = 20

discounted_amount = purchase - (purchase * discount / 100)

if member.lower() == "yes":
    discounted_amount = discounted_amount - (discounted_amount * 5 / 100)

print(f"Final payable amount: NPR {discounted_amount:.2f}")