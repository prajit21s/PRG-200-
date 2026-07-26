inventory = {
    "rice": {"price": 120, "stock": 20},
    "milk": {"price": 90, "stock": 10},
    "bread": {"price": 60, "stock": 15},
    "eggs": {"price": 15, "stock": 30}
}

cart = {
    "rice": 2,
    "milk": 3,
    "eggs": 12
}

def process_order(inventory, cart):
    total_bill = 0

    print("---- Bill ----")

    for item, quantity in cart.items():

        if item in inventory and inventory[item]["stock"] >= quantity:

            price = inventory[item]["price"]
            item_total = price * quantity

            print(f"{item} x{quantity} = NPR {item_total}")

            total_bill += item_total

            inventory[item]["stock"] -= quantity

        else:
            print(f"Sorry, not enough stock for {item}")

    print(f"\nGrand Total: NPR {total_bill}")
    print("----------------")

    print("\nUpdated Inventory:")
    for item, details in inventory.items():
        print(f"{item} = {details['stock']}")

process_order(inventory, cart)