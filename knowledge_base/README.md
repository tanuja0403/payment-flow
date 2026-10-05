# PayFlow Intelligence Knowledge Base

This directory contains domain knowledge used by the PayFlow Intelligence RAG system.

## Structure

### iso20022/

General payment and address concepts related to ISO 20022-style payment messaging.

### address_rules/

Payment-address validation and structured-address guidance.

### rejection_codes/

Application-level payment rejection and validation concepts.

### repair_guidelines/

Guidance for correcting address-related payment-quality problems.

### operational_procedures/

Operational workflows for investigating and repairing payment-quality problems.

## Important Architecture Rule

The knowledge base does not replace deterministic validation.

The deterministic validation engine remains authoritative for:

- Payment validity
- Validation errors
- Validation warnings
- Payment status

The RAG layer provides contextual knowledge to the AI system.

## RAG Flow

Payment
↓
Validation
↓
Validation Error
↓
Retrieval Query
↓
Knowledge Base
↓
Relevant Knowledge
↓
Ollama
↓
Grounded Explanation
↓
Recommendation

## Future Metadata

Documents may eventually include metadata such as:

- source
- category
- topic
- document_type
- version
- country
- rule_type
