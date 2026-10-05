from agent.state import PaymentAgentState


def validation_node(
    state: PaymentAgentState
) -> PaymentAgentState:

    validation_result = state.get(
        "validation_result",
        {}
    )

    if not validation_result:

        return {
            **state,
            "validation_status": "UNKNOWN",
            "error": "No validation result was provided."
        }

    status = str(
        validation_result.get(
            "status",
            ""
        )
    ).upper()

    if status in {
        "VALID",
        "ACCEPTED"
    }:

        validation_status = "VALID"

    elif status in {
        "REJECTED",
        "INVALID"
    }:

        validation_status = "INVALID"

    elif status == "REVIEW":

        validation_status = "REVIEW"

    else:

        # Fall back to the existence of errors.
        errors = validation_result.get(
            "errors",
            []
        )

        if errors:
            validation_status = "INVALID"
        else:
            validation_status = "UNKNOWN"

    return {
        **state,

        "validation_status": validation_status,

        "error": None
    }