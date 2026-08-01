class DeliveryPartner:

    def __init__(self, name, partner_id, deliveries):
        self.name = name
        self.partner_id = partner_id
        self.deliveries = deliveries

    def total_earning(self):
        return 0

    def display(self):
        print(
            f"{self.name} | Deliveries: {self.deliveries} | "
            f"Earning: NPR {self.total_earning()}"
        )


class BikeRider(DeliveryPartner):

    def __init__(self, name, partner_id, deliveries, km_travelled):
        super().__init__(name, partner_id, deliveries)
        self.km_travelled = km_travelled

    def total_earning(self):
        return (self.deliveries * 80) + (self.km_travelled * 5)


class Walker(DeliveryPartner):

    def __init__(self, name, partner_id, deliveries, rainy_deliveries):
        super().__init__(name, partner_id, deliveries)
        self.rainy_deliveries = rainy_deliveries

    def total_earning(self):
        return (self.deliveries * 60) + (self.rainy_deliveries * 50)


class CarDriver(DeliveryPartner):

    def __init__(self, name, partner_id, deliveries, fuel_cost):
        super().__init__(name, partner_id, deliveries)
        self.fuel_cost = fuel_cost

    def total_earning(self):
        return (self.deliveries * 120) - self.fuel_cost


partners = [
    BikeRider("Santosh Rai", "B-01", 15, 42),
    Walker("Kabita Maharjan", "W-01", 18, 5),
    CarDriver("Roshan KC", "C-01", 20, 850)
]

highest = partners[0]

for partner in partners:

    partner.display()

    if partner.total_earning() > highest.total_earning():
        highest = partner

print(f"\nHighest Earner: {highest.name}")