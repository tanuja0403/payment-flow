from sqlalchemy import Column, Integer, String, Text
from database.db import Base


class ValidationResult(Base):
    __tablename__ = "validation_results"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    payment_id = Column(
        String,
        nullable=False,
        index=True
    )

    status = Column(
        String,
        nullable=False
    )

    errors = Column(
        Text,
        nullable=True
    )