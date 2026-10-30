from theatres.models import Theatre, Seat
from decimal import Decimal

# Get existing theatre
theatre = Theatre.objects.get(name="Demo Cinemas")

# Ticket prices
prices = {
    "NORMAL": Decimal("150.00"),
    "PREMIUM": Decimal("250.00"),
    "RECLINER": Decimal("400.00"),
}

# Generate seats
for row in "ABCDEF":

    if row in "ABCD":
        category = "NORMAL"
    elif row == "E":
        category = "PREMIUM"
    else:
        category = "RECLINER"

    for number in range(1, 11):

        Seat.objects.update_or_create(
            theatre=theatre,
            row=row,
            number=number,
            defaults={
                "category": category,
                "price": prices[category]
            }
        )

# Verify results
print("\n----- THEATRE DETAILS -----")
print("Theatre:", theatre.name)

for category in prices:
    count = Seat.objects.filter(
        theatre=theatre,
        category=category
    ).count()

    print(category, ":", count, "seats")

total = Seat.objects.filter(theatre=theatre).count()

revenue = sum(
    seat.price for seat in Seat.objects.filter(theatre=theatre)
)

print("Total seats:", total)
print("Total potential revenue: ₹", revenue)
