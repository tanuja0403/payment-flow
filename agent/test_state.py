from agent.state import PaymentAgentState


def main():

    state: PaymentAgentState = {
        "payment_id": "TEST-001",

        "payment_data": {
            "beneficiary_name": "Test Beneficiary",
            "beneficiary_country": "IN"
        },

        "validation_result": {
            "error_code": "MISSING_BENEFICIARY_ADDRESS",
            "field": "beneficiary_address",
            "message": "Beneficiary address is missing."
        },

        "validation_status": "INVALID",

        "rag_query": "",
        "retrieved_documents": [],

        "ai_analysis": "",
        "ai_sources": [],

        "decision": "",
        "recommended_action": "",

        "requires_human_review": False,
        "human_decision": None,

        "final_status": "",
        "error": None
    }

    print("=" * 60)
    print("LANGGRAPH STATE TEST")
    print("=" * 60)

    print("\nPayment ID:")
    print(state["payment_id"])

    print("\nValidation:")
    print(state["validation_result"])

    print("\nState created successfully.")

    print("=" * 60)


if __name__ == "__main__":
    main()
