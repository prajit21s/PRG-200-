# Foreign Remittance Converter

usd = float(input("Enter amount in USD: "))
exchange_rate = float(input("Enter exchange rate (1 USD to NPR): "))
fee_percent = float(input("Enter service fee percentage: "))

converted_npr = usd * exchange_rate

fee = (fee_percent / 100) * converted_npr

final_amount = converted_npr - fee

print("\n----- Foreign Remittance Summary -----")
print(f"Converted Amount: NPR {converted_npr:.2f}")
print(f"Service Fee: NPR {fee:.2f}")
print(f"Final Amount Received: NPR {final_amount:.2f}")
