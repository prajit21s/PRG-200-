usd = float(input("Enter amount in USD: "))
rate = float(input("Enter exchange rate (1 USD to NPR): "))
fee_percent = float(input("Enter service fee percentage: "))

converted_amount = usd * rate
fee = (fee_percent / 100) * converted_amount
final_amount = converted_amount - fee

print("\n----- Remittance Summary -----")
print(f"Converted Amount: NPR {converted_amount:.2f}")
print(f"Service Fee: NPR {fee:.2f}")
print(f"Final Amount Received: NPR {final_amount:.2f}")