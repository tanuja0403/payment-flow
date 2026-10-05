# Payment Account Validation Rules

## MISSING_ACCOUNT

Error code:
MISSING_ACCOUNT

Meaning:

Required payment account information is missing.

Problematic field:

account

Operational impact:

The payment cannot be processed normally because required account information is unavailable.

Recommended action:

Verify the original payment data and obtain the missing account information.
Revalidate after correction.

## INVALID_ACCOUNT

Error code:
INVALID_ACCOUNT

Meaning:

Account information is present but does not satisfy the configured account-format validation.

Problematic field:

account

Operational impact:

The payment may not be routable or processable until the account information is corrected.

Recommended action:

Verify the account information against the applicable account-format rules.
Correct the account data and revalidate.

## MISSING_CREDITOR_ACCOUNT

Error code:
MISSING_CREDITOR_ACCOUNT

Meaning:

The required creditor or beneficiary account information is missing.

Problematic field:

creditor_account

Operational impact:

The intended beneficiary account cannot be determined reliably.

Recommended action:

Obtain the creditor or beneficiary account information from the trusted payment source.
Revalidate after correction.

## Important

AI must never fabricate an account number, IBAN, or other financial identifier.
