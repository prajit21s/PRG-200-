passwords = ["hello", "Hello123", "H3ll0@World", "12345678", "MyP@ss!"]

special_chars = "!@#$%^&*"

for password in passwords:
    print(f"\nChecking Password: {password}")

    if len(password) < 8:
        print("- Must be at least 8 characters long")

    if not any(char.isupper() for char in password):
        print("- Missing uppercase letter")

    if not any(char.islower() for char in password):
        print("- Missing lowercase letter")

    if not any(char.isdigit() for char in password):
        print("- Missing digit")

    if not any(char in special_chars for char in password):
        print("- Missing special character")

    if (
        len(password) >= 8
        and any(char.isupper() for char in password)
        and any(char.islower() for char in password)
        and any(char.isdigit() for char in password)
        and any(char in special_chars for char in password)
    ):
        print("Strong Password")