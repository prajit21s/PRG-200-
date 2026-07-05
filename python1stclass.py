# ATM Simulation

balance = 50000
correct_pin = "1234"

print("========== WELCOME TO ATM ==========")

# Step 1: Insert Card
insert = input("Insert ATM Card? (yes/no): ").lower()

if insert != "yes":
    print("No card inserted. Transaction cancelled.")
    exit()

# Step 2: Check Card
card = input("Is this a valid ATM card? (yes/no): ").lower()

if card != "yes":
    print("Invalid card!")
    print("Card removed.")
    exit()

# Step 3: Enter PIN
pin = input("Enter your 4-digit PIN: ")

if pin != correct_pin:
    print("Incorrect PIN!")
    print("Card removed.")
    exit()

print("\nPIN Verified Successfully!")

# Step 4: ATM Menu
while True:
    print("\n===== ATM MENU =====")
    print("1. Balance Inquiry")
    print("2. Withdraw Cash")
    print("3. Deposit Money")
    print("4. Exit")

    choice = input("Enter your choice (1-4): ")

    if choice == "1":
        print(f"Your current balance is: Rs. {balance}")

    elif choice == "2":
        amount = float(input("Enter withdrawal amount: Rs. "))

        if amount <= 0:
            print("Invalid amount.")

        elif amount > balance:
            print("Insufficient balance.")

        else:
            balance -= amount
            print("Please collect your cash.")
            print(f"Remaining balance: Rs. {balance}")

    elif choice == "3":
        amount = float(input("Enter deposit amount: Rs. "))

        if amount <= 0:
            print("Invalid amount.")

        else:
            balance += amount
            print("Deposit successful.")
            print(f"Updated balance: Rs. {balance}")

    elif choice == "4":
        print("\nThank you for using our ATM.")
        print("Please collect your card.")
        break

    else:
        print("Invalid choice. Please try again.")