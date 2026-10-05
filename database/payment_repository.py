from database.models import Payment


def get_all_payments(db):
    payments = (
        db.query(Payment)
        .order_by(Payment.id)
        .all()
    )

    return payments


def get_payment_by_id(db, payment_id):
    return (
        db.query(Payment)
        .filter(Payment.payment_id == payment_id)
        .first()
    )


def save_payment(db, payment):
    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment