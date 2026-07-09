
print("----- Trek Expense Splitter -----")

# Money paid by each friend
friend1 = float(input("Enter amount paid by Friend 1: "))
friend2 = float(input("Enter amount paid by Friend 2: "))
friend3 = float(input("Enter amount paid by Friend 3: "))
friend4 = float(input("Enter amount paid by Friend 4: "))
friend5 = float(input("Enter amount paid by Friend 5: "))

total = friend1 + friend2 + friend3 + friend4 + friend5

# Equal share
share = total / 5

print("\nTotal Expense:", total)
print(f"Each friend should pay: Rs. {share:.2f}")

# Friend 1
difference = friend1 - share
if difference > 0:
    print(f"Friend 1 should receive Rs. {difference:.2f}")
elif difference < 0:
    print(f"Friend 1 should pay Rs. {-difference:.2f}")
else:
    print("Friend 1 is settled.")

# Friend 2
difference = friend2 - share
if difference > 0:
    print(f"Friend 2 should receive Rs. {difference:.2f}")
elif difference < 0:
    print(f"Friend 2 should pay Rs. {-difference:.2f}")
else:
    print("Friend 2 is settled.")

# Friend 3
difference = friend3 - share
if difference > 0:
    print(f"Friend 3 should receive Rs. {difference:.2f}")
elif difference < 0:
    print(f"Friend 3 should pay Rs. {-difference:.2f}")
else:
    print("Friend 3 is settled.")

# Friend 4
difference = friend4 - share
if difference > 0:
    print(f"Friend 4 should receive Rs. {difference:.2f}")
elif difference < 0:
    print(f"Friend 4 should pay Rs. {-difference:.2f}")
else:
    print("Friend 4 is settled.")

# Friend 5
difference = friend5 - share
if difference > 0:
    print(f"Friend 5 should receive Rs. {difference:.2f}")
elif difference < 0:
    print(f"Friend 5 should pay Rs. {-difference:.2f}")
else:
    print("Friend 5 is settled.")