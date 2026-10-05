import json
from typing import Any, Dict

import streamlit as st

from rag.rag_pipeline import run_rag


def show_rag_analysis(
    validation_result: Dict[str, Any]
):
    """
    Display dynamic RAG analysis in Streamlit.

    The function accepts the deterministic validation
    result and allows RAG to analyse ALL errors.
    """

    st.subheader(
        "🧠 RAG Knowledge Analysis"
    )

    if not validation_result:

        st.info(
            "No validation result available for RAG."
        )

        return

    with st.spinner(
        "Retrieving payment knowledge and generating analysis..."
    ):

        try:

            result = run_rag(
                validation_result
            )

        except Exception as exc:

            st.error(
                f"RAG analysis failed: {exc}"
            )

            return

    # ---------------------------------------------------------
    # VALIDATION ERRORS
    # ---------------------------------------------------------

    errors = validation_result.get(
        "errors",
        [],
    )

    if isinstance(errors, dict):
        errors = [errors]

    if errors:

        st.write(
            "**Validation Issues Used by RAG**"
        )

        for error in errors:

            if isinstance(error, dict):

                code = error.get(
                    "code",
                    "UNKNOWN",
                )

                field = error.get(
                    "field",
                    "unknown",
                )

                message = error.get(
                    "message",
                    "",
                )

                st.warning(
                    f"**{code}** — `{field}`\n\n"
                    f"{message}"
                )

            else:

                st.warning(
                    str(error)
                )

    # ---------------------------------------------------------
    # OVERALL SUMMARY
    # ---------------------------------------------------------

    st.write(
        "**AI Summary**"
    )

    st.info(
        result.get(
            "overall_summary",
            "Not available.",
        )
    )

    # ---------------------------------------------------------
    # INDIVIDUAL ISSUES
    # ---------------------------------------------------------

    issues = result.get(
        "issues",
        [],
    )

    if issues:

        st.write(
            "**Issue-by-Issue RAG Analysis**"
        )

        for index, issue in enumerate(
            issues,
            start=1,
        ):

            code = issue.get(
                "error_code",
                "UNKNOWN",
            )

            field = issue.get(
                "field",
                "unknown",
            )

            with st.expander(
                f"{index}. {code} — {field}",
                expanded=True,
            ):

                st.write(
                    "**Explanation**"
                )

                st.write(
                    issue.get(
                        "explanation",
                        "Not available.",
                    )
                )

                st.write(
                    "**Relevant Guidance**"
                )

                st.write(
                    issue.get(
                        "relevant_guidance",
                        "Not available.",
                    )
                )

                st.write(
                    "**Recommended Action**"
                )

                st.success(
                    issue.get(
                        "recommended_action",
                        "Not available.",
                    )
                )

    # ---------------------------------------------------------
    # OVERALL RECOMMENDATION
    # ---------------------------------------------------------

    st.write(
        "**Overall Recommendation**"
    )

    st.success(
        result.get(
            "overall_recommendation",
            "Not available.",
        )
    )

    # ---------------------------------------------------------
    # CONFIDENCE
    # ---------------------------------------------------------

    confidence = result.get(
        "confidence"
    )

    if isinstance(
        confidence,
        (int, float),
    ):

        st.metric(
            "AI Confidence",
            f"{confidence:.0%}",
        )

    # ---------------------------------------------------------
    # SOURCES
    # ---------------------------------------------------------

    sources = result.get(
        "sources",
        [],
    )

    if sources:

        st.write(
            "**Knowledge Sources**"
        )

        for source in sources:

            st.code(
                source
            )

    # ---------------------------------------------------------
    # DEBUG / RAW RESULT
    # ---------------------------------------------------------

    with st.expander(
        "View Raw RAG Result"
    ):

        st.json(
            result
        )