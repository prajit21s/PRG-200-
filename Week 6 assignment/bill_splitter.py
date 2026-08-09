import random

random.seed(42)

friends = ["Ramesh", "Sunita", "Bikash", "Anjali", "Dipak"]
total_bill = 3750


def split_bill(friends, total):
    share = total / len(friends)
    return share


def pick_lucky(friends):
    lucky_person = random.choice(friends)
    return lucky_person


def final_summary(friends, total):
    share = split_bill(friends, total)
    lucky = pick_lucky(friends)

    print("Bill Summary")
    print("----------------")

    for person in friends:
        if person == lucky:
            lucky_total = share + 50
            print(f"{person}: NPR {lucky_total:.2f} (Lucky Tax)")
        else:
            print(f"{person}: NPR {share:.2f}")

    print(f"\nLucky person: {lucky}")


final_summary(friends, total_bill)