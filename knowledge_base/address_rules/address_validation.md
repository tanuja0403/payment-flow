# Payment Address Validation Rules

## Purpose

This document defines the conceptual address-quality rules used by PayFlow Intelligence.

The deterministic validation engine remains the authoritative source for deciding whether a payment passes or fails validation.

RAG does not perform the validation.

## Rule 1 — Beneficiary Address Presence

A payment may require beneficiary or creditor address information depending on the applicable payment requirements.

If required address information is absent, the payment may require rejection or manual review.

## Rule 2 — Address Completeness

An address may be considered incomplete when important address components expected by the applicable payment rule are absent.

Examples include:

- Missing country
- Missing city/town
- Missing postal code
- Missing street information

The exact mandatory fields depend on the applicable payment requirements.

## Rule 3 — Country Information

Country information should be represented consistently with the applicable payment standard and processing requirements.

Invalid or missing country information may result in a payment-quality problem.

## Rule 4 — Structured Address

Where structured address information is required or preferred, individual address components should be stored in their appropriate fields rather than being placed entirely into free-form text.

## Rule 5 — Address Consistency

Address components should be internally consistent.

Potential inconsistencies include:

- Country inconsistent with other address information
- Postal information inconsistent with the stated location
- Missing required components
- Conflicting address values

## Rule 6 — Missing Information

Missing address information should not automatically be interpreted as a compliance violation.

The system should identify the actual validation problem and explain its operational significance.

## Rule 7 — Deterministic Validation

The PayFlow validation engine determines whether an address-related validation error exists.

The AI and RAG layers must not invent address errors that were not identified by deterministic validation.

## Example

Validation result:

Field:
beneficiary_address

Error:
MISSING_BENEFICIARY_ADDRESS

The AI should explain the supplied error.

The AI should not independently invent:

INVALID_COUNTRY

unless the deterministic validation result contains that error.
