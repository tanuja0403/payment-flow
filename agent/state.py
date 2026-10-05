from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict


class PaymentAgentState(TypedDict, total=False):
    # Original payment data
    payment_id: str
    payment_data: Dict[str, Any]

    # Deterministic validation
    validation_result: Dict[str, Any]
    validation_status: str

    # RAG
    rag_query: str
    retrieved_documents: List[Dict[str, Any]]

    # AI analysis
    ai_analysis: str
    ai_sources: List[str]

    # Agent decision
    decision: str
    recommended_action: str

    # Human review
    requires_human_review: bool
    human_decision: Optional[str]

    # Final output
    final_status: str
    error: Optional[str]
