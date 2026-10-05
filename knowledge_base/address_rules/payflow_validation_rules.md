# PayFlow Intelligence Validation Rules

## Purpose

This document describes the relationship between deterministic validation and AI/RAG analysis.

## Core Principle

Deterministic validation determines whether a payment contains a validation problem.

AI and RAG explain the problem.

## Validation Flow

Payment Data
↓
Normalization
↓
Deterministic Validation
↓
Validation Errors
↓
Payment Status

## Payment Status

VALID

The payment contains no blocking validation errors.

REJECTED

The payment contains one or more blocking validation errors.

REVIEW

The payment requires manual investigation according to configured business rules.

## Address Validation

Address-related validation may identify:

- Missing beneficiary address
- Incomplete beneficiary address
- Missing country
- Invalid country
- Other configured address-quality problems

## AI Constraint

The AI must only analyse validation problems supplied by the deterministic validation engine.

Example:

Validation:

MISSING_BENEFICIARY_ADDRESS

Correct AI behavior:

"The payment was rejected because the required beneficiary address information is missing."

Incorrect AI behavior:

"The payment was rejected because the beneficiary country is invalid."

The second statement is unsupported unless the validation result also contains an invalid-country error.

## RAG Constraint

RAG provides domain knowledge.

RAG does not determine payment validity.

## Source of Truth

Payment validity:
Deterministic Validation Engine

Domain Explanation:
RAG + AI

Operational Decision:
Operations User / Configured Workflow
