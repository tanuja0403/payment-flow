# Structured Payment Address Guidance

## Purpose

Structured addresses represent individual address components separately.

This allows downstream systems to process and validate address information more consistently.

## Typical Components

A structured address may contain:

- Street name
- Building number
- Postal code
- Town or city
- Country
- Additional address information

## Structured vs Unstructured

Structured:

Street = Main Street
Building Number = 10
Postal Code = 10115
Town = Berlin
Country = DE

Unstructured:

10 Main Street, Berlin 10115, Germany

The appropriate representation depends on the applicable payment standard and processing requirements.

## PayFlow Intelligence

PayFlow can use address structure as part of data-quality analysis.

Potential issues include:

- Address components missing
- Address components placed in the wrong field
- Excessive use of unstructured information
- Country information missing
- Inconsistent address components

## RAG Usage

When a deterministic validation result identifies an address-structure problem, the RAG system can retrieve relevant guidance from this document.

The retrieved information should support the AI explanation and recommendation.

RAG must not replace the deterministic validation engine.
