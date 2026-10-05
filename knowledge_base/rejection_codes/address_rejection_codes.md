# Payment Address Rejection Codes

## Purpose

This document contains PayFlow Intelligence project-level address-related rejection concepts.

These identifiers are application-level concepts unless explicitly mapped to an authoritative external payment standard.

## MISSING_BENEFICIARY_ADDRESS

### Meaning

Required beneficiary address information was not found in the normalized payment data.

### Typical Field

beneficiary_address

### Operational Impact

The payment may require correction before it can proceed.

### Suggested Operational Action

Verify the original payment message and obtain the required beneficiary address information.

### RAG Explanation

The RAG system can retrieve address requirements and repair guidance when this error is encountered.

---

## INCOMPLETE_BENEFICIARY_ADDRESS

### Meaning

Beneficiary address information exists but one or more expected components are missing.

### Typical Field

beneficiary_address

### Operational Impact

The payment may require additional information or manual review.

### Suggested Operational Action

Determine which address component is required and correct the payment data.

---

## INVALID_COUNTRY

### Meaning

The country information supplied for the relevant address does not satisfy the application's configured validation rule.

### Typical Field

beneficiary_address.country

### Operational Impact

The payment may require correction.

### Suggested Operational Action

Verify the country information against the applicable payment requirement.

---

## MISSING_COUNTRY

### Meaning

Required country information is absent.

### Typical Field

beneficiary_address.country

### Operational Impact

The payment may require correction or manual review depending on applicable rules.

### Suggested Operational Action

Obtain and populate the required country information.

---

## IMPORTANT

These application-level concepts must not be represented as official ISO 20022 rejection codes unless an authoritative mapping has been established.

The deterministic validation engine remains the source of truth for whether the error actually exists.
