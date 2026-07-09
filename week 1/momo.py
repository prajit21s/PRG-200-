# Take input from the user
cost_price = float(input("Enter cost price per plate (Rs): "))
selling_price = float(input("Enter selling price per plate (Rs): "))
plates_sold = float(input("Enter number of plates sold: "))

# Calculate total revenue
total_revenue = selling_price * plates_sold

# Calculate total cost
total_cost = cost_price * plates_sold

# Calculate total profit
total_profit = total_revenue - total_cost

# Calculate profit margin percentage
profit_margin = (total_profit / total_revenue) * 100

# Display the results
print("\n----- Momo Shop Daily Profit -----")
print(f"Total Revenue: Rs. {total_revenue:.2f}")
print(f"Total Cost: Rs. {total_cost:.2f}")
print(f"Total Profit: Rs. {total_profit:.2f}")
print(f"Profit Margin: {profit_margin:.2f}%")
