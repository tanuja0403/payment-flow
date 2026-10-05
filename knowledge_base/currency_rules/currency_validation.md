
# Payment Currency Validation Rules

## MISSING_CURRENCY

Error code:
MISSING_CURRENCY

Meaning:

Currency information is missing from the payment.

Problematic field:

currency

Operational impact:

The payment amount cannot be interpreted reliably without the required currency information.

Recommended action:

Verify the original payment source and provide the required currency.
Revalidate the payment.

## INVALID_CURRENCY

Error code:
INVALID_CURRENCY

Meaning:

The supplied currency does not satisfy the configured currency-code format.

Problematic field:

currency

Operational impact:

The payment cannot proceed until the currency information is corrected.

Recommended action:

Verify the supplied currency against the configured supported currency-code rules.
Correct the currency and revalidate.

## UNSUPPORTED_CURRENCY

Error code:
UNSUPPORTED_CURRENCY

Meaning:

The currency is present and formatted correctly but is not supported by the configured payment processing rules.

Problematic field:

currency

Operational impact:

The payment cannot proceed through the configured processing route.

Recommended action:

Verify whether the currency is supported for the payment context.
If appropriate, obtain an acceptable currency from the source system or route the payment according to operational procedures.

## Important

Do not invent a replacement currency.
AI should only recommend a specific currency if trusted payment data explicitly provides it.
