cost_price = float(input("Enter cost price per plate: "))
selling_price = float(input("Enter selling price per plate: "))
plates_sold = int(input("Enter number of plates sold: "))

total_revenue = selling_price * plates_sold
total_cost = cost_price * plates_sold
profit = total_revenue - total_cost
profit_margin = (profit / total_revenue) * 100

print("\n----- Momo Shop Profit -----")
print(f"Total Revenue: NPR {total_revenue:.2f}")
print(f"Total Cost: NPR {total_cost:.2f}")
print(f"Profit: NPR {profit:.2f}")
print(f"Profit Margin: {profit_margin:.2f}%")