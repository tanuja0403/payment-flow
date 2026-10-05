# General Payment Validation Rules

## MISSING_PAYMENT_ID

Error code:
MISSING_PAYMENT_ID

Meaning:

The payment does not contain a required payment identifier.

Problematic field:

payment_id

Operational impact:

The payment cannot be reliably identified or tracked.

Recommended action:

Verify the source payment data and provide the required identifier.

## INVALID_DATE

Error code:
INVALID_DATE

Meaning:

The payment date does not satisfy the configured date-format or validation requirements.

Problematic field:

payment_date

Operational impact:

The payment may not be processed until the date information is corrected.

Recommended action:

Verify the original payment date and correct its representation.
Revalidate after correction.

## DUPLICATE_PAYMENT

Error code:
DUPLICATE_PAYMENT

Meaning:

The payment reference or identifying information matches an existing payment according to the configured duplicate-detection rules.

Problematic field:

transaction_reference

Operational impact:

Processing the payment may result in duplicate transaction handling.

Recommended action:

Verify whether the payment is genuinely new.
Do not automatically remove or bypass duplicate detection.

## MISSING_CRITICAL_DATA_ELEMENT

Error code:
MISSING_CRITICAL_DATA_ELEMENT

Meaning:

A data element required for reliable payment processing is missing.

Operational impact:

The payment cannot safely proceed until the required information is available.

Recommended action:

Identify the missing field from the deterministic validation result.
Obtain the information from a trusted source and revalidate.

## MALFORMED_VALUE

Error code:
MALFORMED_VALUE

Meaning:

A supplied payment value does not follow the expected structural format.

Operational impact:

The affected payment field cannot be reliably interpreted.

Recommended action:

Identify the exact problematic field from the validation result.
Correct its format and revalidate.

## INVALID_VALUE

Error code:
INVALID_VALUE

Meaning:

A supplied value does not satisfy the configured validation rule.

Operational impact:

The payment may not proceed until the invalid value is corrected.

Recommended action:

Use the deterministic validation result to identify the exact field and rule.
Correct the data and revalidate.
