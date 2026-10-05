from database.db import engine, Base
from database.models import Payment
from database.validation_models import ValidationResult


Base.metadata.create_all(
    bind=engine
)


print(
    "Database tables created successfully!"
)