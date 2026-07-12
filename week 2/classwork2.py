import re

email_list = []
accepted_emails = []
rejected_emails = []

count = int(input("How many email addresses do you want to check? "))

for i in range(count):
    address = input(f"Email {i+1}: ")
    email_list.append(address)

email_pattern = r'^[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

for address in email_list:
    result = re.match(email_pattern, address)

    if result:
        accepted_emails.append(address)
    else:
        rejected_emails.append(address)

print("\nEmails Accepted:")
for item in accepted_emails:
    print("-", item)

print("\nEmails Rejected:")
for item in rejected_emails:
    print("-", item)