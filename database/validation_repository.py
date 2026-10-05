import json

from database.validation_models import ValidationResult


def save_validation_result(db, result):
    errors = result.get("errors", [])
    if not isinstance(errors, str):
        errors = json.dumps(errors, default=str)

    validation_result = ValidationResult(
        payment_id=str(result["payment_id"]),
        status=result["status"],
        errors=errors
    )

    db.add(validation_result)
    db.commit()

    return validation_result


def get_all_validation_results(db):
    validation_results = (
        db.query(ValidationResult)
        .order_by(ValidationResult.id)
        .all()
    )

    return validation_results