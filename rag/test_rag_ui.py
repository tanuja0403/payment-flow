import streamlit as st

from rag.rag_ui import show_rag_analysis


st.title("PayFlow Intelligence - RAG Test")

validation_result = {
    "error_code": "MISSING_BENEFICIARY_ADDRESS",
    "field": "beneficiary_address",
    "message": (
        "Required beneficiary address information "
        "is missing."
    )
}

show_rag_analysis(validation_result)
