TAX_RATE = 0.13


def apply_discount(price, percent):
    discount = price * percent / 100
    return price - discount


def apply_tax(price):
    tax = price * TAX_RATE
    return price + tax


def final_price(price, discount_pct):
    discounted_price = apply_discount(price, discount_pct)
    total_price = apply_tax(discounted_price)

    return total_price