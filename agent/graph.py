from langgraph.graph import StateGraph, END

from agent.state import PaymentAgentState

from agent.nodes import (
    inspect_validation_node,
    classify_errors_node,
    create_rag_query_node,
    run_rag_node,
    human_review_node,
    final_agent_node,
)


def route_after_classification(state):

    decision = state.get("decision")

    if decision == "RAG_ANALYSIS":
        return "create_rag_query"

    if decision == "HUMAN_REVIEW":
        return "human_review"

    return "final"


def build_agent_graph():

    workflow = StateGraph(PaymentAgentState)

    workflow.add_node("inspect_validation", inspect_validation_node)

    workflow.add_node("classify_errors", classify_errors_node)

    workflow.add_node("create_rag_query", create_rag_query_node)

    workflow.add_node("run_rag", run_rag_node)

    workflow.add_node("human_review", human_review_node)

    workflow.add_node("final", final_agent_node)

    workflow.set_entry_point("inspect_validation")

    workflow.add_edge("inspect_validation", "classify_errors")

    workflow.add_conditional_edges(
        "classify_errors",
        route_after_classification,
        {
            "create_rag_query": "create_rag_query",
            "human_review": "human_review",
            "final": "final",
        },
    )

    workflow.add_edge("create_rag_query", "run_rag")

    workflow.add_edge("run_rag", "final")

    workflow.add_edge("human_review", "final")

    workflow.add_edge("final", END)

    return workflow.compile()


agent_graph = build_agent_graph()
