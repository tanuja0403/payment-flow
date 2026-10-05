from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.dependencies import get_db
from database.validation_repository import get_all_validation_results


router = APIRouter(
    prefix="/validation",
    tags=["Validation"]
)


@router.get("/")
def get_validation_results(db: Session = Depends(get_db)):
    validation_results = get_all_validation_results(db)

    return [
        {
            "id": result.id,
            "payment_id": result.payment_id,
            "status": result.status,
            "errors": result.errors
        }
        for result in validation_results
    ]