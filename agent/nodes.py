from typing import Dict, Any

from rag.rag_pipeline import run_rag


def inspect_validation_node(state: Dict[str, Any]) -> Dict[str, Any]:

    validation_result = state.get("validation_result", {})

    issues = validation_result.get("errors", [])

    if not issues:
        return {
            "decision": "APPROVE",
            "final_status": "APPROVED",
            "requires_human_review": False,
        }

    return {
        "decision": "ANALYZE_ERRORS",
        "final_status": "PENDING_ANALYSIS",
    }


def classify_errors_node(state: Dict[str, Any]) -> Dict[str, Any]:

    validation_result = state.get("validation_result", {})

    errors = validation_result.get("errors", [])

    if not errors:
        return {
            "decision": "APPROVE",
            "final_status": "APPROVED",
        }

    error_codes = [error.get("code", error.get("error_code", "")) for error in errors]

    high_risk_errors = {
        "SANCTIONS_MATCH",
        "FRAUD_SUSPECTED",
        "COMPLIANCE_VIOLATION",
        "DUPLICATE_PAYMENT",
    }

    if any(code in high_risk_errors for code in error_codes):
        return {
            "decision": "HUMAN_REVIEW",
            "requires_human_review": True,
            "final_status": "REVIEW_REQUIRED",
        }

    return {
        "decision": "RAG_ANALYSIS",
        "requires_human_review": False,
        "final_status": "PENDING_ANALYSIS",
    }


def create_rag_query_node(state: Dict[str, Any]) -> Dict[str, Any]:

    validation_result = state.get("validation_result", {})

    errors = validation_result.get("errors", [])

    error_codes = [error.get("code", error.get("error_code", "")) for error in errors]

    fields = [error.get("field", "") for error in errors]

    rag_query = (
        "Find payment validation rules, "
        "correction procedures and operational "
        "guidance for these errors: "
        f"{', '.join(error_codes)}. "
        f"Affected fields: {', '.join(fields)}."
    )

    return {
        "rag_query": rag_query,
        "decision": "RUN_RAG",
    }


def run_rag_node(state: Dict[str, Any]) -> Dict[str, Any]:

    validation_result = state.get("validation_result", {})

    try:

        result = run_rag(validation_result)

        return {
            "ai_analysis": result,
            "ai_sources": result.get("sources", []),
            "decision": "ANALYSIS_COMPLETE",
            "final_status": "ANALYSIS_COMPLETE",
        }

    except Exception as exc:

        return {
            "error": str(exc),
            "decision": "ERROR",
            "final_status": "ERROR",
        }


def human_review_node(state: Dict[str, Any]) -> Dict[str, Any]:

    return {
        "decision": "HUMAN_REVIEW",
        "requires_human_review": True,
        "final_status": "REVIEW_REQUIRED",
        "recommended_action": ("Payment requires human review."),
    }


def final_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:

    return {
        "decision": state.get("decision", "UNKNOWN"),
        "final_status": state.get("final_status", "UNKNOWN"),
        "recommended_action": state.get("recommended_action", ""),
        "ai_analysis": state.get("ai_analysis"),
        "ai_sources": state.get("ai_sources", []),
        "requires_human_review": state.get("requires_human_review", False),
        "error": state.get("error"),
    }
