from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.dependencies import get_db
from database.payment_repository import (
    get_all_payments,
    get_payment_by_id
)


router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)


@router.get("/")
def get_payments(db: Session = Depends(get_db)):
    payments = get_all_payments(db)

    return [
        {
            "id": payment.id,
            "payment_id": payment.payment_id,
            "amount": payment.amount,
            "currency": payment.currency,
            "beneficiary": payment.beneficiary
        }
        for payment in payments
    ]


@router.get("/{payment_id}")
def get_payment(payment_id: str, db: Session = Depends(get_db)):
    payment = get_payment_by_id(db, payment_id)

    if payment is None:
        return {
            "message": "Payment not found",
            "payment_id": payment_id
        }

    return {
        "id": payment.id,
        "payment_id": payment.payment_id,
        "amount": payment.amount,
        "currency": payment.currency,
        "beneficiary": payment.beneficiary
    }