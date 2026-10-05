from validation.validators import validate_payment


# ==========================================
# TEST PAYMENTS
# ==========================================

test_payments = [

    # Completely valid payment
    {
        "payment_id": "P0001",
        "amount": "1500",
        "currency": "USD",
        "beneficiary": "John Smith"
    },

    # Invalid amount
    {
        "payment_id": "P0002",
        "amount": "-500",
        "currency": "EUR",
        "beneficiary": "ABC Ltd"
    },

    # Invalid currency
    {
        "payment_id": "P0003",
        "amount": "2500",
        "currency": "XYZ",
        "beneficiary": "Global Trading Co"
    },

    # Invalid beneficiary
    {
        "payment_id": "P0004",
        "amount": "3000",
        "currency": "GBP",
        "beneficiary": "12345"
    },

    # Multiple errors
    {
        "payment_id": "INVALID",
        "amount": "-100",
        "currency": "XYZ",
        "beneficiary": "###"
    }
]


# ==========================================
# RUN VALIDATION
# ==========================================

for payment in test_payments:

    result = validate_payment(payment)

    print("=" * 50)

    print(
        "Payment ID:",
        result["payment_id"]
    )

    print(
        "Status:",
        result["status"]
    )

    if result["errors"]:

        print("Errors:")

        for error in result["errors"]:
            print("-", error)

    else:

        print("Errors: None")


print("=" * 50)