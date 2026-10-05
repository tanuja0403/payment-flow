from agent.graph import agent_graph


def main():

    validation_result = {
        "payment_id": "AGENT-TEST-001",
        "status": "REJECTED",
        "errors": [
            {
                "field": "amount",
                "code": "MISSING_AMOUNT",
                "message": "Payment amount is missing.",
            },
            {
                "field": "currency",
                "code": "MISSING_CURRENCY",
                "message": "Payment currency is missing.",
            },
            {
                "field": "creditor_account",
                "code": "MISSING_ACCOUNT",
                "message": "Creditor account is missing.",
            },
        ],
        "warnings": [],
    }

    initial_state = {
        "payment_id": "AGENT-TEST-001",
        "validation_result": validation_result,
    }

    print("=" * 70)
    print("PAYFLOW LANGGRAPH AGENT TEST")
    print("=" * 70)

    result = agent_graph.invoke(initial_state)

    print()
    print("AGENT DECISION:")
    print(result.get("decision"))

    print()
    print("FINAL STATUS:")
    print(result.get("final_status"))

    print()
    print("RAG QUERY:")
    print(result.get("rag_query"))

    print()
    print("HUMAN REVIEW:")
    print(result.get("requires_human_review"))

    print()
    print("AI ANALYSIS:")
    print(result.get("ai_analysis"))

    print()
    print("AI SOURCES:")
    print(result.get("ai_sources"))

    print()
    print("=" * 70)
    print("AGENT TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
