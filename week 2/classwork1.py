import re

emails = []
valid = []
invalid = []

n = int(input("Enter the number of emails: "))

for i in range(n):
    email = input(f"Enter email {i+1}: ")
    emails.append(email)

# Regular expression for email validation
pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

for email in emails:
    if re.fullmatch(pattern, email):
        valid.append(email)
    else:
        invalid.append(email)

print("\nValid Emails:")
for email in valid:
    print(email)

print("\nInvalid Emails:")
for email in invalid:
    print(email)