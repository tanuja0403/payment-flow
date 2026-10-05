import re


# ============================================================
# PAYMENT ID VALIDATION
# ============================================================

def validate_payment_id(payment_id):

    errors = []

    if payment_id is None:

        errors.append({
            "field": "payment_id",
            "category": "MISSING_PAYMENT_ID",
            "message": "Payment ID is missing."
        })

        return errors

    payment_id = str(payment_id).strip()

    if payment_id == "":

        errors.append({
            "field": "payment_id",
            "category": "EMPTY_PAYMENT_ID",
            "message": "Payment ID is empty."
        })

        return errors

    if not re.fullmatch(
        r"P\d{4}",
        payment_id
    ):

        errors.append({
            "field": "payment_id",
            "category": "INVALID_PAYMENT_ID",
            "message": (
                "Payment ID must follow the format P0001."
            )
        })

    return errors


# ============================================================
# AMOUNT VALIDATION
# ============================================================

def validate_amount(amount):

    errors = []

    if amount is None:

        errors.append({
            "field": "amount",
            "category": "MISSING_AMOUNT",
            "message": "Amount is missing."
        })

        return errors

    amount = str(amount).strip()

    if amount == "":

        errors.append({
            "field": "amount",
            "category": "EMPTY_AMOUNT",
            "message": "Amount is empty."
        })

        return errors

    try:

        amount_value = float(amount)

    except ValueError:

        errors.append({
            "field": "amount",
            "category": "NON_NUMERIC_AMOUNT",
            "message": "Amount must be numeric."
        })

        return errors

    if amount_value <= 0:

        errors.append({
            "field": "amount",
            "category": "INVALID_AMOUNT",
            "message": (
                "Amount must be greater than 0."
            )
        })

    return errors


# ============================================================
# CURRENCY VALIDATION
# ============================================================

def validate_currency(currency):

    errors = []

    valid_currencies = {
        "USD",
        "EUR",
        "GBP",
        "INR",
        "JPY",
        "AUD",
        "CAD",
        "CHF",
        "SGD",
        "AED"
    }

    if currency is None:

        errors.append({
            "field": "currency",
            "category": "MISSING_CURRENCY",
            "message": "Currency is missing."
        })

        return errors

    currency = str(currency).strip().upper()

    if currency == "":

        errors.append({
            "field": "currency",
            "category": "EMPTY_CURRENCY",
            "message": "Currency is empty."
        })

        return errors

    if not re.fullmatch(
        r"[A-Z]{3}",
        currency
    ):

        errors.append({
            "field": "currency",
            "category": "INVALID_CURRENCY_FORMAT",
            "message": (
                "Currency must be a 3-letter code."
            )
        })

        return errors

    if currency not in valid_currencies:

        errors.append({
            "field": "currency",
            "category": "UNSUPPORTED_CURRENCY",
            "message": (
                f"Unsupported currency: {currency}"
            )
        })

    return errors


# ============================================================
# BENEFICIARY VALIDATION
# ============================================================

def validate_beneficiary(beneficiary):

    errors = []

    if beneficiary is None:

        errors.append({
            "field": "beneficiary",
            "category": "MISSING_BENEFICIARY",
            "message": (
                "Beneficiary is missing."
            )
        })

        return errors

    beneficiary = str(
        beneficiary
    ).strip()

    if beneficiary == "":

        errors.append({
            "field": "beneficiary",
            "category": "EMPTY_BENEFICIARY",
            "message": (
                "Beneficiary is empty."
            )
        })

        return errors

    alphabetic_characters = re.findall(
        r"[A-Za-z]",
        beneficiary
    )

    if len(alphabetic_characters) < 2:

        errors.append({
            "field": "beneficiary",
            "category": "INVALID_BENEFICIARY",
            "message": (
                "Beneficiary must contain at least "
                "two alphabetic characters."
            )
        })

        return errors

    if not re.fullmatch(
        r"[A-Za-z\s.'&-]+",
        beneficiary
    ):

        errors.append({
            "field": "beneficiary",
            "category": "INVALID_BENEFICIARY_CHARACTERS",
            "message": (
                "Beneficiary contains invalid characters."
            )
        })

    return errors


# ============================================================
# COMPLETE PAYMENT VALIDATION
# ============================================================

def validate_payment(payment):

    errors = []


    # --------------------------------------------------------
    # PAYMENT ID
    # --------------------------------------------------------

    errors.extend(
        validate_payment_id(
            payment.get("payment_id")
        )
    )


    # --------------------------------------------------------
    # AMOUNT
    # --------------------------------------------------------

    errors.extend(
        validate_amount(
            payment.get("amount")
        )
    )


    # --------------------------------------------------------
    # CURRENCY
    # --------------------------------------------------------

    errors.extend(
        validate_currency(
            payment.get("currency")
        )
    )


    # --------------------------------------------------------
    # BENEFICIARY
    # --------------------------------------------------------

    errors.extend(
        validate_beneficiary(
            payment.get("beneficiary")
        )
    )


    # --------------------------------------------------------
    # SIMPLE ERROR MESSAGES
    # --------------------------------------------------------

    error_messages = []

    for error in errors:

        error_messages.append(
            error["message"]
        )


    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    if errors:

        status = "INVALID"

    else:

        status = "VALID"


    # --------------------------------------------------------
    # FINAL VALIDATION RESULT
    # --------------------------------------------------------

    return {

        "payment_id":
            payment.get("payment_id"),

        "status":
            status,

        "errors":
            error_messages,

        "field_errors":
            errors
    }