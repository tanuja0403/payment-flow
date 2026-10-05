# Beneficiary and Creditor Validation Rules

## MISSING_CREDITOR

Error code:
MISSING_CREDITOR

Meaning:

Required creditor or beneficiary information is missing.

Problematic field:

creditor_name

Operational impact:

The payment does not contain sufficient beneficiary identification.

Recommended action:

Verify the original payment information and provide the required creditor or beneficiary information.
Revalidate after correction.

## MISSING_BENEFICIARY

Error code:
MISSING_BENEFICIARY

Meaning:

Required beneficiary information is missing.

Problematic field:

beneficiary

Operational impact:

The payment cannot reliably identify the intended recipient.

Recommended action:

Obtain the beneficiary information from the trusted source.
Do not invent beneficiary information.
Revalidate after correction.

## MISSING_BENEFICIARY_ADDRESS

Error code:
MISSING_BENEFICIARY_ADDRESS

Meaning:

Required beneficiary address information is missing.

Problematic field:

beneficiary_address

Operational impact:

The payment may require correction or manual review depending on the configured payment requirements.

Recommended action:

Verify the source payment information and obtain the required address information.
Revalidate after correction.

## Important

AI must not assume that every payment rejection is an address problem.

The actual deterministic validation error is authoritative.
