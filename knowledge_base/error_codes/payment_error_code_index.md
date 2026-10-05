# Payment Validation Error Code Index

This document maps payment validation error codes to their domains.

## Amount

MISSING_AMOUNT
INVALID_AMOUNT
NEGATIVE_AMOUNT
ZERO_AMOUNT

Domain:
Amount validation

## Currency

MISSING_CURRENCY
INVALID_CURRENCY
UNSUPPORTED_CURRENCY

Domain:
Currency validation

## Account

MISSING_ACCOUNT
INVALID_ACCOUNT
MISSING_CREDITOR_ACCOUNT

Domain:
Account validation

## Beneficiary / Creditor

MISSING_CREDITOR
MISSING_BENEFICIARY
MISSING_BENEFICIARY_ADDRESS

Domain:
Beneficiary and creditor validation

## Payment Identification

MISSING_PAYMENT_ID
DUPLICATE_PAYMENT

Domain:
Payment identification and duplicate detection

## Date

INVALID_DATE

Domain:
Payment date validation

## General Data Quality

MALFORMED_VALUE
INVALID_VALUE
MISSING_CRITICAL_DATA_ELEMENT

Domain:
General payment data validation

## Address

INCOMPLETE_ADDRESS
MISSING_COUNTRY
MISSING_POSTAL_CODE
UNSTRUCTURED_ADDRESS
INVALID_COUNTRY_CODE

Domain:
Address and geographic data quality

## Retrieval Principle

When a validation error code is supplied to the AI/RAG system:

1. Match the exact error code when possible.
2. Retrieve knowledge from the corresponding domain.
3. Use the validation field and message as additional retrieval context.
4. Do not retrieve unrelated domain guidance merely because the payment was rejected.
5. The deterministic validation result remains authoritative.
