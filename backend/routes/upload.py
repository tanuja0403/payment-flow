from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import csv
import json
import xml.etree.ElementTree as ET

from database.db import SessionLocal
from database.models import Payment
from database.payment_repository import get_payment_by_id
from database.validation_repository import save_validation_result
from validation.validators import validate_payment


router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)


UPLOAD_DIRECTORY = Path("data/uploads")
UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)


def parse_csv(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)


def parse_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def parse_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    payments = []

    for payment in root.findall(".//Payment"):
        payments.append({
            "payment_id": payment.findtext("payment_id"),
            "amount": payment.findtext("amount"),
            "currency": payment.findtext("currency"),
            "beneficiary": payment.findtext("beneficiary")
        })

    return payments


def parse_file(file_path, file_extension):

    if file_extension == ".csv":
        return parse_csv(file_path)

    if file_extension == ".json":
        return parse_json(file_path)

    if file_extension == ".xml":
        return parse_xml(file_path)

    raise ValueError("Unsupported file format.")


@router.post("/")
async def upload_payment_file(file: UploadFile = File(...)):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="File name is missing."
        )

    file_extension = Path(file.filename).suffix.lower()

    allowed_extensions = {
        ".csv",
        ".json",
        ".xml"
    }

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Use CSV, JSON, or XML."
        )

    file_contents = await file.read()

    if not file_contents:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    file_path = UPLOAD_DIRECTORY / file.filename

    with open(file_path, "wb") as output_file:
        output_file.write(file_contents)

    try:
        payment_data = parse_file(
            file_path,
            file_extension
        )

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to parse file: {error}"
        )

    if not payment_data:
        raise HTTPException(
            status_code=400,
            detail="No payment records found in the uploaded file."
        )

    validation_results = []

    for payment in payment_data:

        result = validate_payment(payment)

        validation_results.append(result)

    valid_count = sum(
        1
        for result in validation_results
        if result["status"] == "VALID"
    )

    invalid_count = sum(
        1
        for result in validation_results
        if result["status"] == "INVALID"
    )

    db = SessionLocal()

    stored_payment_count = 0
    duplicate_count = 0
    validation_stored_count = 0

    try:

        # Save validation results
        for result in validation_results:

            save_validation_result(
                db,
                result
            )

            validation_stored_count += 1

        # Save only valid payments
        for payment_data_item, result in zip(
            payment_data,
            validation_results
        ):

            if result["status"] != "VALID":
                continue

            payment_id = str(
                payment_data_item.get("payment_id")
            ).strip()

            existing_payment = get_payment_by_id(
                db,
                payment_id
            )

            if existing_payment:
                duplicate_count += 1
                continue

            payment = Payment(
                payment_id=payment_id,
                amount=float(
                    payment_data_item.get("amount")
                ),
                currency=str(
                    payment_data_item.get("currency")
                ).strip().upper(),
                beneficiary=str(
                    payment_data_item.get("beneficiary")
                ).strip()
            )

            db.add(payment)
            stored_payment_count += 1

        db.commit()

    except Exception as error:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Database processing failed: {error}"
        )

    finally:
        db.close()

    return {
        "filename": file.filename,
        "file_type": file_extension.replace(".", "").upper(),
        "total_payments": len(payment_data),
        "valid_payments": valid_count,
        "invalid_payments": invalid_count,
        "validation_results_stored": validation_stored_count,
        "valid_payments_stored": stored_payment_count,
        "duplicate_payments": duplicate_count
    }