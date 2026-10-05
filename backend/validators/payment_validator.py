# ============================================================
# PAYMENT VALIDATION ENGINE
# ============================================================


# ============================================================
# REQUIRED PAYMENT FIELDS
# ============================================================

REQUIRED_PAYMENT_FIELDS = [
    "payment_id",
    "amount",
    "currency",
    "beneficiary"
]


# ============================================================
# REQUIRED BENEFICIARY ADDRESS FIELDS
# ============================================================

REQUIRED_ADDRESS_FIELDS = [
    "street",
    "building",
    "postal_code",
    "town",
    "country"
]


# ============================================================
# VALID CURRENCIES
# ============================================================

COMMON_CURRENCIES = {
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


# ============================================================
# TEXT VALIDATION
# ============================================================

def is_empty(value):
    """
    Return True when a value is missing or empty.
    """

    if value is None:
        return True

    if isinstance(value, str):
        return not value.strip()

    return False


# ============================================================
# PAYMENT ID VALIDATION
# ============================================================

def validate_payment_id(payment, errors):
    """
    Validate payment identifier.
    """

    payment_id = payment.get(
        "payment_id"
    )

    if is_empty(payment_id):

        errors.append(
            "Payment ID is missing"
        )


# ============================================================
# AMOUNT VALIDATION
# ============================================================

def validate_amount(payment, errors):
    """
    Validate transaction amount.
    """

    amount = payment.get(
        "amount"
    )

    if amount is None:

        errors.append(
            "Amount is missing or invalid"
        )

        return

    try:

        amount = float(amount)

    except (
        ValueError,
        TypeError
    ):

        errors.append(
            "Amount must be numeric"
        )

        return

    if amount <= 0:

        errors.append(
            "Amount must be greater than zero"
        )


# ============================================================
# CURRENCY VALIDATION
# ============================================================

def validate_currency(payment, errors):
    """
    Validate currency.
    """

    currency = payment.get(
        "currency"
    )

    if is_empty(currency):

        errors.append(
            "Currency is missing"
        )

        return

    currency = str(
        currency
    ).strip().upper()

    if len(currency) != 3:

        errors.append(
            "Currency must be a 3-letter ISO code"
        )

        return

    if currency not in COMMON_CURRENCIES:

        errors.append(
            f"Unsupported currency: {currency}"
        )


# ============================================================
# BENEFICIARY VALIDATION
# ============================================================

def validate_beneficiary(payment, errors):
    """
    Validate beneficiary name.
    """

    beneficiary = payment.get(
        "beneficiary"
    )

    if is_empty(beneficiary):

        errors.append(
            "Beneficiary name is missing"
        )


# ============================================================
# BENEFICIARY ADDRESS VALIDATION
# ============================================================

def validate_beneficiary_address(
    payment,
    errors
):
    """
    Validate beneficiary address fields.

    If the address is supplied through AdrLine,
    we preserve it as unstructured data.

    The structured fields are validated when
    they are expected to be present.
    """

    address_line = payment.get(
        "address_line"
    )

    # --------------------------------------------------------
    # If an unstructured address exists, don't immediately
    # reject it. It can later be processed by the AI layer.
    # --------------------------------------------------------

    if not is_empty(address_line):

        return

    # --------------------------------------------------------
    # Structured address validation
    # --------------------------------------------------------

    for field in REQUIRED_ADDRESS_FIELDS:

        value = payment.get(
            field
        )

        if is_empty(value):

            field_name = field.replace(
                "_",
                " "
            )

            errors.append(
                f"Beneficiary {field_name} is missing"
            )


# ============================================================
# COUNTRY VALIDATION
# ============================================================

def validate_country(
    country,
    field_name,
    errors
):
    """
    Validate a country code.
    """

    if is_empty(country):

        errors.append(
            f"{field_name} is missing"
        )

        return

    country = str(
        country
    ).strip().upper()

    if len(country) != 2:

        errors.append(
            f"{field_name} must be a 2-letter country code"
        )


# ============================================================
# DEBTOR VALIDATION
# ============================================================

def validate_debtor(payment, errors):
    """
    Validate debtor information.
    """

    debtor = payment.get(
        "debtor"
    )

    if is_empty(debtor):

        errors.append(
            "Debtor name is missing"
        )


# ============================================================
# MAIN VALIDATION FUNCTION
# ============================================================

def validate_payment(payment):
    """
    Validate one normalized payment.

    Returns:

        {
            "payment_id": "...",
            "status": "VALID",
            "validation_score": 100,
            "errors": [],
            "warnings": []
        }
    """

    errors = []
    warnings = []

    # --------------------------------------------------------
    # Basic validations
    # --------------------------------------------------------

    validate_payment_id(
        payment,
        errors
    )

    validate_amount(
        payment,
        errors
    )

    validate_currency(
        payment,
        errors
    )

    validate_beneficiary(
        payment,
        errors
    )

    # --------------------------------------------------------
    # Address validation
    # --------------------------------------------------------

    validate_beneficiary_address(
        payment,
        errors
    )

    # --------------------------------------------------------
    # Debtor validation
    # --------------------------------------------------------

    validate_debtor(
        payment,
        errors
    )

    # --------------------------------------------------------
    # Debtor country
    # --------------------------------------------------------

    debtor_country = payment.get(
        "debtor_country"
    )

    if debtor_country:

        validate_country(
            debtor_country,
            "Debtor country",
            errors
        )

    # --------------------------------------------------------
    # Beneficiary country
    # --------------------------------------------------------

    beneficiary_country = payment.get(
        "country"
    )

    if beneficiary_country:

        validate_country(
            beneficiary_country,
            "Beneficiary country",
            errors
        )

    # --------------------------------------------------------
    # Determine status
    # --------------------------------------------------------

    if errors:

        status = "INVALID"

    else:

        status = "VALID"

    # --------------------------------------------------------
    # Validation score
    # --------------------------------------------------------

    total_checks = 10

    failed_checks = min(
        len(errors),
        total_checks
    )

    validation_score = round(
        (
            (total_checks - failed_checks)
            / total_checks
        ) * 100
    )

    # --------------------------------------------------------
    # Result
    # --------------------------------------------------------

    return {

        "payment_id":
            payment.get("payment_id"),

        "status":
            status,

        "validation_score":
            validation_score,

        "errors":
            errors,

        "warnings":
            warnings
    }


# ============================================================
# VALIDATE MULTIPLE PAYMENTS
# ============================================================

def validate_payments(payments):
    """
    Validate a list of payments.
    """

    results = []

    for payment in payments:

        result = validate_payment(
            payment
        )

        results.append(
            result
        )

    return results