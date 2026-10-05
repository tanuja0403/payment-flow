from agent.state import PaymentAgentState
from rag.payment_retriever import retrieve_for_payment


def rag_node(state: PaymentAgentState) -> PaymentAgentState:
    """
    Retrieve knowledge based on the ACTUAL validation
    result contained in the LangGraph state.

    No error code is hardcoded here.
    """

    validation_result = state.get("validation_result", {})

    if not validation_result:
        return {
            **state,
            "retrieved_documents": [],
            "rag_query": "",
            "error": "No validation result available for RAG."
        }

    # ---------------------------------------------------------
    # Handle the validation structure used by the application.
    # ---------------------------------------------------------

    errors = validation_result.get("errors", [])

    # If errors is a string, keep it as a single error.
    if isinstance(errors, str):
        errors = [errors]

    # If the backend provides a single error object.
    if isinstance(errors, dict):
        errors = [errors]

    # ---------------------------------------------------------
    # Build a generic validation result for RAG.
    # ---------------------------------------------------------

    rag_validation = {
        "payment_id": validation_result.get(
            "payment_id"
        ),

        "status": validation_result.get(
            "status"
        ),

        "errors": errors,

        "warnings": validation_result.get(
            "warnings",
            []
        )
    }

    # ---------------------------------------------------------
    # Retrieve knowledge for the ACTUAL error(s).
    # ---------------------------------------------------------

    documents = retrieve_for_payment(
        rag_validation,
        k=4
    )

    # ---------------------------------------------------------
    # Convert LangChain documents into state data.
    # ---------------------------------------------------------

    retrieved_documents = []

    for document in documents:

        retrieved_documents.append(
            {
                "content": document.page_content,

                "source": document.metadata.get(
                    "source",
                    "unknown"
                ),

                "category": document.metadata.get(
                    "category",
                    "unknown"
                )
            }
        )

    # ---------------------------------------------------------
    # Create a readable RAG query.
    # ---------------------------------------------------------

    error_text = []

    for error in errors:

        if isinstance(error, dict):

            code = error.get(
                "code",
                error.get("error_code", "")
            )

            field = error.get(
                "field",
                ""
            )

            message = error.get(
                "message",
                ""
            )

            error_text.append(
                f"Code: {code}\n"
                f"Field: {field}\n"
                f"Message: {message}"
            )

        else:

            error_text.append(
                str(error)
            )

    rag_query = (
        "Payment validation errors:\n"
        + "\n\n".join(error_text)
        + "\n\nRetrieve relevant payment rules, "
          "explanations, operational impact, and "
          "repair guidance."
    )

    return {
        **state,

        "rag_query": rag_query,

        "retrieved_documents": retrieved_documents,

        "error": None
    }