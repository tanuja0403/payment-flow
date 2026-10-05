import json
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from rag.payment_retriever import (
    normalize_error,
    retrieve_for_errors,
)

# ============================================================
# CONFIGURATION
# ============================================================

LLM_MODEL = "llama3.2"


# ============================================================
# PYDANTIC STRUCTURED OUTPUT MODELS
# ============================================================


class IssueAnalysis(BaseModel):
    error_code: str = Field(description="Original validation error code")

    field: str = Field(description="Field affected by the validation error")

    explanation: str = Field(
        description="Explanation of why the validation error occurred"
    )

    relevant_guidance: str = Field(
        description="Relevant guidance from the retrieved knowledge"
    )

    recommended_action: str = Field(description="Recommended operational correction")


class PaymentAnalysis(BaseModel):
    payment_id: str = Field(description="Payment identifier")

    status: str = Field(description="Payment validation status")

    issues: List[IssueAnalysis] = Field(
        description="Analysis of every validation error"
    )

    overall_summary: str = Field(
        description="Overall summary of the payment validation result"
    )

    overall_recommendation: str = Field(description="Overall recommended action")

    confidence: float = Field(
        description="Confidence between 0 and 1",
        ge=0.0,
        le=1.0,
    )


# ============================================================
# ERROR NORMALIZATION
# ============================================================


def normalize_errors(validation_result: Dict[str, Any]) -> List[Dict[str, str]]:

    errors = validation_result.get("errors", [])

    if errors is None:
        errors = []

    if isinstance(errors, dict):
        errors = [errors]

    if isinstance(errors, str):

        return [
            {
                "field": str(
                    validation_result.get(
                        "field",
                        "",
                    )
                ),
                "code": str(
                    validation_result.get(
                        "error_code",
                        "",
                    )
                ),
                "message": errors,
            }
        ]

    normalized = []

    for error in errors:

        item = normalize_error(error)

        if item.get("code") or item.get("field") or item.get("message"):
            normalized.append(item)

    # Backward compatibility
    if not normalized and (
        validation_result.get("error_code")
        or validation_result.get("field")
        or validation_result.get("message")
    ):

        normalized.append(
            {
                "field": str(
                    validation_result.get(
                        "field",
                        "",
                    )
                ),
                "code": str(
                    validation_result.get(
                        "error_code",
                        "",
                    )
                ),
                "message": str(
                    validation_result.get(
                        "message",
                        "",
                    )
                ),
            }
        )

    return normalized


# ============================================================
# BUILD RAG CONTEXT
# ============================================================


def build_context(retrieved: Dict[str, List[Dict[str, Any]]]) -> str:

    sections = []

    for error_code, documents in retrieved.items():

        sections.append(f"ERROR: {error_code}")

        if not documents:

            sections.append("No specific knowledge was retrieved.")

            continue

        for index, document in enumerate(
            documents,
            start=1,
        ):

            sections.append(f"SOURCE {index}: " f"{document.get('source', 'unknown')}")

            sections.append(
                document.get(
                    "content",
                    "",
                )
            )

    return "\n\n".join(sections)


# ============================================================
# LANGCHAIN PROMPT
# ============================================================


def build_prompt():

    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are the PayFlow Intelligence payment-analysis assistant.

Analyze payment validation errors using:

1. The deterministic validation result.
2. The retrieved PayFlow knowledge base.

IMPORTANT RULES:

- The deterministic validation result is the source of truth.
- Analyze EVERY validation error supplied.
- Do NOT invent additional errors.
- Do NOT change error codes.
- Do NOT invent payment values.
- Do NOT invent beneficiary information.
- Do NOT assume every error is an address error.
- Use retrieved knowledge to explain each error.
- Give a practical recommended action for each error.
- Use the knowledge retrieved for the specific error whenever possible.
- If relevant knowledge is unavailable, say:
  "Information is unavailable."
- Do not make unsupported compliance claims.

The final answer must contain exactly one issue
for every validation error supplied.

The error_code and field must match the
original validation result exactly.

Confidence must be between 0 and 1.
""",
            ),
            (
                "human",
                """
VALIDATION RESULT:

{validation_result}

RETRIEVED KNOWLEDGE:

{context}
""",
            ),
        ]
    )


# ============================================================
# LANGCHAIN + OLLAMA STRUCTURED OUTPUT
# ============================================================


def call_llm(
    prompt,
    validation_result: Dict[str, Any],
    context: str,
) -> Dict[str, Any]:

    llm = ChatOllama(
        model=LLM_MODEL,
        temperature=0,
    )

    # LangChain structured output
    structured_llm = llm.with_structured_output(PaymentAnalysis)

    chain = prompt | structured_llm

    response = chain.invoke(
        {
            "validation_result": json.dumps(
                validation_result,
                indent=2,
                ensure_ascii=False,
            ),
            "context": context,
        }
    )

    # Pydantic object → normal dictionary
    if isinstance(response, PaymentAnalysis):

        return response.model_dump()

    # Safety fallback
    if isinstance(response, dict):

        return response

    raise ValueError("Unexpected structured output returned by Ollama.")


# ============================================================
# COLLECT SOURCES
# ============================================================


def collect_sources(retrieved: Dict[str, List[Dict[str, Any]]]) -> List[str]:

    sources = []

    for documents in retrieved.values():

        for document in documents:

            source = document.get(
                "source",
                "unknown",
            )

            if source not in sources:

                sources.append(source)

    return sources


# ============================================================
# VALIDATE STRUCTURED RESULT
# ============================================================


def validate_result(
    result: Dict[str, Any],
    validation_result: Dict[str, Any],
) -> Dict[str, Any]:

    errors = normalize_errors(validation_result)

    returned_issues = result.get("issues", [])

    # --------------------------------------------------------
    # Ensure every original error exists
    # --------------------------------------------------------

    existing_codes = {issue.get("error_code") for issue in returned_issues}

    for error in errors:

        if error["code"] not in existing_codes:

            returned_issues.append(
                {
                    "error_code": error["code"],
                    "field": error["field"],
                    "explanation": (
                        "AI analysis was not generated " "for this validation error."
                    ),
                    "relevant_guidance": ("Information is unavailable."),
                    "recommended_action": (
                        "Review the deterministic "
                        "validation result and correct "
                        "the affected field."
                    ),
                }
            )

    result["issues"] = returned_issues

    # --------------------------------------------------------
    # Force original error code and field
    # --------------------------------------------------------

    error_lookup = {error["code"]: error for error in errors}

    for issue in result["issues"]:

        code = issue.get("error_code", "")

        if code in error_lookup:

            issue["error_code"] = code

            issue["field"] = error_lookup[code]["field"]

    # --------------------------------------------------------
    # Keep payment ID from deterministic result
    # --------------------------------------------------------

    if validation_result.get("payment_id"):

        result["payment_id"] = validation_result["payment_id"]

    # --------------------------------------------------------
    # Keep actual status
    # --------------------------------------------------------

    if validation_result.get("status"):

        result["status"] = validation_result["status"]

    return result


# ============================================================
# MAIN RAG PIPELINE
# ============================================================


def run_rag(validation_result: Dict[str, Any]) -> Dict[str, Any]:

    # --------------------------------------------------------
    # STEP 1
    # Extract ALL validation errors
    # --------------------------------------------------------

    errors = normalize_errors(validation_result)

    # --------------------------------------------------------
    # No errors
    # --------------------------------------------------------

    if not errors:

        return {
            "payment_id": validation_result.get(
                "payment_id",
                "",
            ),
            "status": validation_result.get(
                "status",
                "VALID",
            ),
            "issues": [],
            "overall_summary": ("No validation errors were supplied."),
            "overall_recommendation": ("No correction is required."),
            "confidence": 1.0,
            "sources": [],
        }

    # --------------------------------------------------------
    # STEP 2
    # Retrieve knowledge for EVERY error
    # --------------------------------------------------------

    retrieved = retrieve_for_errors(
        errors,
        k_per_error=4,
    )

    # --------------------------------------------------------
    # STEP 3
    # Build RAG context
    # --------------------------------------------------------

    context = build_context(retrieved)

    # --------------------------------------------------------
    # STEP 4
    # Build LangChain prompt
    # --------------------------------------------------------

    prompt = build_prompt()

    # --------------------------------------------------------
    # STEP 5
    # Call LangChain + Ollama
    # --------------------------------------------------------

    try:

        result = call_llm(
            prompt,
            validation_result,
            context,
        )

        result = validate_result(
            result,
            validation_result,
        )

    except Exception as exc:

        print()
        print("=" * 70)
        print("LANGCHAIN / OLLAMA ERROR")
        print("=" * 70)
        print(str(exc))
        print("=" * 70)
        print()

        result = {
            "payment_id": validation_result.get(
                "payment_id",
                "",
            ),
            "status": validation_result.get(
                "status",
                "REJECTED",
            ),
            "issues": [
                {
                    "error_code": error["code"],
                    "field": error["field"],
                    "explanation": ("AI analysis is unavailable."),
                    "relevant_guidance": (
                        "Retrieved knowledge was available, "
                        "but the local LLM could not generate "
                        "the structured analysis."
                    ),
                    "recommended_action": (
                        "Review the deterministic "
                        "validation result and correct "
                        "the affected field."
                    ),
                }
                for error in errors
            ],
            "overall_summary": ("AI analysis is unavailable."),
            "overall_recommendation": (
                "Use the deterministic validation " "result for operational handling."
            ),
            "confidence": 0.0,
        }

    # --------------------------------------------------------
    # STEP 6
    # Add RAG sources
    # --------------------------------------------------------

    result["sources"] = collect_sources(retrieved)

    return result


# ============================================================
# TERMINAL OUTPUT
# ============================================================


def print_result(
    validation_result: Dict[str, Any],
    result: Dict[str, Any],
) -> None:

    print()
    print("=" * 70)
    print("PAYFLOW - LANGCHAIN STRUCTURED RAG ANALYSIS")
    print("=" * 70)

    print()
    print("PAYMENT ID:")

    print(
        validation_result.get(
            "payment_id",
            "UNKNOWN",
        )
    )

    print()
    print("VALIDATION ERRORS")
    print("-" * 70)

    errors = normalize_errors(validation_result)

    for error in errors:

        print(f"{error['code']} | " f"{error['field']} | " f"{error['message']}")

    print()
    print("AI ANALYSIS")
    print("-" * 70)

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        )
    )

    print()
    print("=" * 70)


# ============================================================
# TEST
# ============================================================


def main():

    validation_result = {
        "payment_id": "TEST-MULTI-001",
        "status": "REJECTED",
        "errors": [
            {
                "field": "amount",
                "code": "MISSING_AMOUNT",
                "message": ("Payment amount is missing."),
            },
            {
                "field": "currency",
                "code": "MISSING_CURRENCY",
                "message": ("Payment currency is missing."),
            },
            {
                "field": "creditor_account",
                "code": "MISSING_ACCOUNT",
                "message": ("Creditor account is missing."),
            },
        ],
        "warnings": [],
    }

    result = run_rag(validation_result)

    print_result(
        validation_result,
        result,
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()
