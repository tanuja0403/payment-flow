from database.db import SessionLocal
from database.payment_repository import get_all_payments


db = SessionLocal()

try:

    payments = get_all_payments(db)

    print(f"Found {len(payments)} payment(s).")

    for payment in payments:

        print(
            payment.payment_id,
            payment.amount,
            payment.currency,
            payment.beneficiary
        )

finally:

    db.close()
    