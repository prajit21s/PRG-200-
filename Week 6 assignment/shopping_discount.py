from discount import final_price, TAX_RATE

products = [
    ("Laptop", 85000, 10),
    ("Headphones", 4500, 15),
    ("Phone Case", 800, 5),
    ("USB Cable", 600, 0)
]

print(f"VAT Rate: {TAX_RATE * 100}%")
print("----------------------------")

for name, price, discount in products:

    final = final_price(price, discount)

    print(f"Product: {name}")
    print(f"Original Price: NPR {price:.2f}")
    print(f"Final Price: NPR {final:.2f}")
    print()