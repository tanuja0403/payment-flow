# ISO 20022 Payment Address Structure

## Purpose

This document describes payment-address concepts relevant to PayFlow Intelligence.

PayFlow Intelligence uses payment-address knowledge to explain data-quality problems detected during deterministic validation.

## Address Information

Payment messages can contain information identifying the postal address of a party involved in a payment.

Relevant address information can include:

- Street name
- Building number
- Postal code
- Town or city
- Country
- Additional address information

The exact address requirements depend on the payment message, applicable market rules, payment scheme, and participating financial institutions.

## Structured Address

A structured address represents address information using separate fields.

Conceptually:

- Street
- Building number
- Postal code
- Town
- Country

Structured address information is easier for systems to validate, process, standardise, and analyse.

## Unstructured Address

An unstructured address represents address information as free-form text.

Unstructured information may be more difficult for automated systems to validate consistently.

## PayFlow Intelligence Relevance

PayFlow Intelligence should distinguish between:

1. Missing address information
2. Incomplete address information
3. Poorly structured address information
4. Invalid address values
5. Address information that requires operational review

## Important Limitation

This document is project knowledge and is not a replacement for the official ISO 20022 specification or a bank-specific payment rulebook.

Where a specific regulatory, scheme, or bank requirement applies, the applicable authoritative source should be consulted.

