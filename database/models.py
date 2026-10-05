from sqlalchemy import Column, Integer, String, Float
from database.db import Base


class Payment(Base):

    __tablename__ = "payments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    payment_id = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    amount = Column(
        Float,
        nullable=False
    )

    currency = Column(
        String,
        nullable=False
    )

    beneficiary = Column(
        String,
        nullable=False
    )