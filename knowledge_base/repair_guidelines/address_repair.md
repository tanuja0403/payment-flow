# Beneficiary Address Repair Guidelines

## Purpose

This document provides operational guidance for correcting beneficiary-address data-quality problems.

## General Repair Process

When an address-related payment error is identified:

1. Identify the validation error.
2. Identify the problematic field.
3. Review the original payment information.
4. Determine what information is missing or incorrect.
5. Obtain the required information from an appropriate source.
6. Correct the payment data.
7. Revalidate the payment.
8. Record the correction and validation result.

## Missing Beneficiary Address

If the beneficiary address is missing:

- Verify whether address information exists in the original payment instruction.
- Determine whether the applicable processing requirement requires the address.
- Obtain the required information.
- Populate the appropriate payment field.
- Revalidate the payment.

## Incomplete Address

If the address exists but is incomplete:

- Identify the missing component.
- Verify the expected address structure.
- Obtain the missing information.
- Correct the relevant field.
- Revalidate.

## Incorrect Country

If country information is invalid:

- Verify the original payment information.
- Confirm the correct country.
- Apply the appropriate country representation.
- Revalidate the payment.

## Do Not Guess

Operations users and AI systems should not invent missing beneficiary information.

If required information is unavailable, the system should state that the information is unavailable.

## AI Recommendation Principle

An AI recommendation should be based on:

- Deterministic validation result
- Payment field
- Retrieved knowledge
- Available payment information

The AI should not fabricate a corrected address.
