class BankAccount:

    def __init__(self, name, account_number, balance=0):
        self.name = name
        self.account_number = account_number
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):

        if amount > self.balance:
            print(f"{self.name}: Insufficient funds")

        else:
            self.balance -= amount

    def get_balance(self):
        print(f"{self.name} - NPR {self.balance}")


a1 = BankAccount("Ramesh Thapa", "A001", 5000)
a2 = BankAccount("Sunita Karki", "A002", 0)
a3 = BankAccount("Bikash Rai", "A003", 12000)

a2.deposit(3000)
a3.withdraw(15000)
a1.withdraw(2000)

print("\nFinal Balances")
a1.get_balance()
a2.get_balance()
a3.get_balance()