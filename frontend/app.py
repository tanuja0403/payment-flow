import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from rag.rag_ui import show_rag_analysis

import pandas as pd
import requests
import streamlit as st

# ============================================================
# CONFIGURATION
# ============================================================

API_BASE_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8000").rstrip("/")
REQUEST_TIMEOUT = int(os.getenv("FASTAPI_TIMEOUT", "30"))
UPLOAD_TIMEOUT = int(os.getenv("FASTAPI_UPLOAD_TIMEOUT", "180"))


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="PayFlow Intelligence",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# PROFESSIONAL LIGHT UI STYLING
# ============================================================

st.markdown(
    """
    <style>
    /* ---------- Global ---------- */
    .stApp {
        background: #f5f7fb;
        color: #172b4d;
    }

    [data-testid="stAppViewContainer"] {
        background: #f5f7fb;
    }

    .main .block-container {
        max-width: 1450px;
        padding: 2rem 3rem 4rem 3rem;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    /* ---------- Typography ---------- */
    h1, h2, h3, h4, h5, h6 {
        color: #172b4d !important;
        font-weight: 700 !important;
    }

    p, span, div {
        color: inherit;
    }

    .stMarkdown p {
        color: #526581;
    }

    [data-testid="stCaptionContainer"] {
        color: #6b7a90 !important;
    }

    /* ---------- Navigation ---------- */
    [data-testid="stRadio"] > div {
        gap: 0.35rem;
        background: #ffffff;
        border: 1px solid #e1e7f0;
        border-radius: 12px;
        padding: 6px;
        box-shadow: 0 2px 8px rgba(23, 43, 77, 0.04);
    }

    [data-testid="stRadio"] label {
        color: #344563 !important;
        font-weight: 600 !important;
        padding: 7px 13px !important;
        border-radius: 8px;
    }

    [data-testid="stRadio"] label p {
        color: #344563 !important;
        font-weight: 600 !important;
    }

    /* ---------- Form labels ---------- */
    [data-testid="stWidgetLabel"] label,
    [data-testid="stWidgetLabel"] p,
    label {
        color: #344563 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }

    /* ---------- Inputs ---------- */
    [data-baseweb="input"] {
        background: #ffffff !important;
        border-radius: 10px !important;
    }

    [data-baseweb="input"] > div {
        background: #ffffff !important;
        border: 1px solid #d5dce8 !important;
        border-radius: 10px !important;
        box-shadow: none !important;
    }

    [data-baseweb="input"] input {
        color: #172b4d !important;
        -webkit-text-fill-color: #172b4d !important;
        background: #ffffff !important;
        font-size: 0.95rem !important;
    }

    [data-baseweb="input"] input::placeholder {
        color: #8a97aa !important;
        -webkit-text-fill-color: #8a97aa !important;
    }

    /* Disabled payment-detail fields must remain readable */
    [data-baseweb="input"] input:disabled {
        color: #172b4d !important;
        -webkit-text-fill-color: #172b4d !important;
        opacity: 1 !important;
        cursor: default;
    }

    /* ---------- Select boxes ---------- */
    [data-baseweb="select"] > div {
        background: #ffffff !important;
        border: 1px solid #d5dce8 !important;
        border-radius: 10px !important;
        min-height: 46px !important;
        box-shadow: none !important;
    }

    [data-baseweb="select"] span {
        color: #172b4d !important;
    }

    [data-baseweb="select"] svg {
        fill: #526581 !important;
    }

    [data-baseweb="popover"],
    [data-baseweb="menu"] {
        background: #ffffff !important;
    }

    [role="option"] {
        color: #172b4d !important;
        background: #ffffff !important;
    }

    [role="option"]:hover {
        background: #eef3ff !important;
    }

    /* ---------- Buttons ---------- */
    .stButton > button {
        border-radius: 9px !important;
        min-height: 42px;
        font-weight: 600 !important;
        border: 1px solid #d5dce8 !important;
        background: #ffffff !important;
        color: #24436f !important;
    }

    .stButton > button p {
        color: #24436f !important;
    }

    .stButton > button:hover {
        border-color: #356ae6 !important;
        background: #eef3ff !important;
        color: #214fae !important;
    }

    .stButton > button[kind="primary"] {
        background: #356ae6 !important;
        border-color: #356ae6 !important;
        color: #ffffff !important;
    }

    .stButton > button[kind="primary"] p {
        color: #ffffff !important;
    }

    /* ---------- Cards ---------- */
    .pf-card {
        background: #ffffff;
        border: 1px solid #e1e7f0;
        border-radius: 14px;
        padding: 20px 22px;
        margin: 8px 0 18px 0;
        box-shadow: 0 3px 12px rgba(23, 43, 77, 0.05);
    }

    .pf-card-title {
        color: #172b4d !important;
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .pf-card-subtitle {
        color: #6b7a90 !important;
        font-size: 0.9rem;
    }

    /* ---------- Metrics ---------- */
    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e1e7f0;
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 2px 8px rgba(23, 43, 77, 0.04);
    }

    [data-testid="stMetricLabel"] {
        color: #6b7a90 !important;
    }

    [data-testid="stMetricLabel"] p {
        color: #6b7a90 !important;
    }

    [data-testid="stMetricValue"] {
        color: #172b4d !important;
    }

    /* ---------- Tables ---------- */
    [data-testid="stDataFrame"] {
        border: 1px solid #e1e7f0;
        border-radius: 10px;
        overflow: hidden;
    }

    /* ---------- File uploader ---------- */
    [data-testid="stFileUploader"] {
        background: #ffffff;
        border: 1px dashed #b8c3d6;
        border-radius: 12px;
        padding: 10px;
    }

    [data-testid="stFileUploader"] section {
        background: #ffffff !important;
    }

    [data-testid="stFileUploader"] small {
        color: #6b7a90 !important;
    }

    /* ---------- Alerts / RAG cards ---------- */
    /* ---------- Alerts / RAG cards ---------- */
    [data-testid="stAlert"],
    [data-testid="stAlert"] > div,
    [data-testid="stAlert"] [role="alert"] {
        background: #ffffff !important;
        background-color: #ffffff !important;
        border: 1px solid #d8e0eb !important;
        border-radius: 10px !important;
        color: #172b4d !important;
        box-shadow: 0 2px 8px rgba(23, 43, 77, 0.04) !important;
    }

    [data-testid="stAlert"] * ,
    [data-testid="stAlert"] p,
    [data-testid="stAlert"] span,
    [data-testid="stAlert"] div,
    [data-testid="stAlert"] li {
        color: #172b4d !important;
        -webkit-text-fill-color: #172b4d !important;
    }

    [data-testid="stAlert"] p,
    [data-testid="stAlert"] span,
    [data-testid="stAlert"] div,
    [data-testid="stAlert"] li {
        color: #172b4d !important;
    }

    [data-testid="stAlert"] svg {
        fill: #526581 !important;
        color: #526581 !important;
    }

    /* RAG validation issue cards */
    [data-testid="stAlert"] [data-testid="stMarkdownContainer"] {
        color: #172b4d !important;
    }

    [data-testid="stAlert"] [data-testid="stMarkdownContainer"] p {
        color: #172b4d !important;
        font-weight: 500 !important;
        line-height: 1.55 !important;
    }

    /* ---------- Expanders ---------- */
    [data-testid="stExpander"] {
        background: #ffffff;
        border: 1px solid #e1e7f0;
        border-radius: 10px;
    }

    /* ---------- Dividers ---------- */
    hr {
        border: none !important;
        border-top: 1px solid #e1e7f0 !important;
        margin: 24px 0 !important;
    }

    /* ---------- Code / JSON ---------- */
    [data-testid="stJson"] {
        border-radius: 10px;
    }

    /* ---------- Sidebar, if opened ---------- */
    [data-testid="stSidebar"] {
        background: #0b2345 !important;
    }

    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    /* ---------- Scrollbar ---------- */
    ::-webkit-scrollbar {
        width: 7px;
        height: 7px;
    }

    ::-webkit-scrollbar-track {
        background: #f5f7fb;
    }

    ::-webkit-scrollbar-thumb {
        background: #c5cfdd;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# CUSTOM ERROR
# ============================================================


class APIClientError(Exception):
    pass


# ============================================================
# SAFE / NORMALIZATION HELPERS
# ============================================================

MISSING = object()


def safe_value(value: Any, default: str = "") -> str:
    """Convert backend values into safe Streamlit display values."""
    if value is None:
        return default

    if isinstance(value, (list, tuple, set)):
        return ", ".join(safe_value(v) for v in value)

    if isinstance(value, dict):
        try:
            return json.dumps(value, ensure_ascii=False, default=str)
        except Exception:
            return str(value)

    return str(value)


def as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def first_value(
    data: Dict[str, Any],
    keys: List[str],
    default: Any = "",
) -> Any:
    """
    Look for a field in the object and common backend wrappers.

    This prevents the UI from showing blank values when the backend
    wraps data inside payment/payment_data/data/details objects.
    """
    if not isinstance(data, dict):
        return default

    containers = [data]

    for wrapper in (
        "payment",
        "payment_data",
        "data",
        "details",
        "original_data",
        "current_data",
    ):
        value = data.get(wrapper)
        if isinstance(value, dict):
            containers.append(value)

    for container in containers:
        for key in keys:
            value = container.get(key, MISSING)

            if value is not MISSING and value not in (None, ""):
                return value

    return default


def person_name(value: Any) -> str:
    """
    Handle beneficiary/debtor values that may be either a string
    or a nested object.
    """
    if isinstance(value, dict):
        for key in (
            "name",
            "full_name",
            "beneficiary_name",
            "creditor_name",
            "debtor_name",
            "display_name",
        ):
            if value.get(key):
                return safe_value(value[key])

        return safe_value(value)

    return safe_value(value)


def normalize_status(value: Any) -> str:
    status = safe_value(value, "UNKNOWN").strip().upper()

    aliases = {
        "VALID": "VALID",
        "ACCEPTED": "VALID",
        "SUCCESS": "VALID",
        "COMPLETED": "VALID",
        "INVALID": "REJECTED",
        "FAILED": "REJECTED",
        "FAILURE": "REJECTED",
        "REJECTED": "REJECTED",
        "PENDING": "PENDING",
        "UNDER REVIEW": "UNDER_REVIEW",
        "UNDER_REVIEW": "UNDER_REVIEW",
        "IN_REVIEW": "UNDER_REVIEW",
    }

    return aliases.get(status, status or "UNKNOWN")


def normalize_payment(payment: Dict[str, Any]) -> Dict[str, str]:
    beneficiary = first_value(
        payment,
        [
            "beneficiary",
            "beneficiary_name",
            "creditor_name",
            "creditor",
            "payee_name",
        ],
    )

    debtor = first_value(
        payment,
        [
            "debtor_name",
            "debtor",
            "payer_name",
            "originator_name",
        ],
    )

    return {
        "payment_id": safe_value(
            first_value(
                payment,
                ["payment_id", "instruction_id", "instr_id", "id"],
            )
        ),
        "amount": safe_value(
            first_value(
                payment,
                ["amount", "instructed_amount", "payment_amount"],
            )
        ),
        "currency": safe_value(
            first_value(
                payment,
                ["currency", "currency_code", "ccy"],
            )
        ),
        "beneficiary": person_name(beneficiary),
        "debtor_name": person_name(debtor),
        "debtor_account": safe_value(
            first_value(
                payment,
                [
                    "debtor_account",
                    "debtor_iban",
                    "payer_account",
                ],
            )
        ),
        "creditor_account": safe_value(
            first_value(
                payment,
                [
                    "creditor_account",
                    "creditor_iban",
                    "beneficiary_account",
                ],
            )
        ),
        "beneficiary_address": safe_value(
            first_value(
                payment,
                [
                    "beneficiary_address",
                    "creditor_address",
                    "payee_address",
                ],
            )
        ),
        "created_at": safe_value(
            first_value(
                payment,
                ["created_at", "timestamp", "created"],
            )
        ),
    }


def normalize_validation(result: Dict[str, Any]) -> Dict[str, str]:
    result = as_dict(result)

    errors = result.get("errors")

    if errors is None:
        errors = result.get("validation_errors")

    if errors is None:
        errors = result.get("validation_message", "")

    warnings = result.get("warnings")

    if warnings is None:
        warnings = result.get("validation_warnings", "")

    return {
        "payment_id": safe_value(
            first_value(
                result,
                ["payment_id", "instruction_id", "id"],
            )
        ),
        "status": normalize_status(
            first_value(
                result,
                ["status", "validation_status", "result"],
            )
        ),
        "errors": safe_value(errors),
        "warnings": safe_value(warnings),
        "created_at": safe_value(
            first_value(
                result,
                ["created_at", "timestamp", "created"],
            )
        ),
    }


def normalize_ai(result: Dict[str, Any]) -> Dict[str, str]:
    result = as_dict(result)

    return {
        "payment_id": safe_value(
            first_value(
                result,
                ["payment_id", "instruction_id", "id"],
            )
        ),
        "status": normalize_status(
            first_value(
                result,
                ["status", "ai_status", "analysis_status"],
            )
        ),
        "severity": safe_value(
            first_value(
                result,
                ["severity", "ai_severity"],
                "UNKNOWN",
            )
        ).upper(),
        "rejection_reason": safe_value(
            first_value(
                result,
                [
                    "rejection_reason",
                    "ai_rejection_reason",
                    "reason",
                ],
            )
        ),
        "root_cause": safe_value(
            first_value(
                result,
                ["root_cause", "ai_root_cause"],
            )
        ),
        "problematic_field": safe_value(
            first_value(
                result,
                [
                    "problematic_field",
                    "ai_problematic_field",
                    "field",
                ],
            )
        ),
        "recommendation": safe_value(
            first_value(
                result,
                [
                    "recommendation",
                    "ai_recommendation",
                    "suggested_correction",
                ],
            )
        ),
        "explanation": safe_value(
            first_value(
                result,
                [
                    "explanation",
                    "ai_explanation",
                    "analysis",
                ],
            )
        ),
        "confidence": safe_value(
            first_value(
                result,
                [
                    "confidence",
                    "ai_confidence",
                    "confidence_score",
                ],
            )
        ),
    }


def normalize_audit(log: Dict[str, Any]) -> Dict[str, str]:
    log = as_dict(log)

    return {
        "event_type": safe_value(
            first_value(
                log,
                [
                    "event_type",
                    "event",
                    "type",
                    "action",
                ],
                "UNKNOWN",
            )
        ).upper(),
        "event_status": safe_value(
            first_value(
                log,
                [
                    "event_status",
                    "status",
                    "result",
                ],
                "UNKNOWN",
            )
        ).upper(),
        "payment_id": safe_value(
            first_value(
                log,
                [
                    "payment_id",
                    "instruction_id",
                    "id",
                ],
                "-",
            )
        ),
        "description": safe_value(
            first_value(
                log,
                [
                    "description",
                    "message",
                    "details_summary",
                ],
                "",
            )
        ),
        "details": safe_value(
            first_value(
                log,
                [
                    "details",
                    "metadata",
                    "payload",
                ],
                "",
            )
        ),
        "created_at": safe_value(
            first_value(
                log,
                [
                    "created_at",
                    "timestamp",
                    "created",
                    "time",
                ],
                "",
            )
        ),
    }


# ============================================================
# API CLIENT
# ============================================================


def _response_error(response: requests.Response) -> str:
    try:
        payload = response.json()

        if isinstance(payload, dict):
            detail = (
                payload.get("detail") or payload.get("message") or payload.get("error")
            )

            if detail:
                return safe_value(detail)

    except Exception:
        pass

    return response.text[:1000] or "Unknown backend error."


def api_get(
    endpoint: str,
    timeout: int = REQUEST_TIMEOUT,
) -> Any:
    try:
        response = requests.get(
            f"{API_BASE_URL}{endpoint}",
            timeout=timeout,
        )

    except requests.exceptions.ConnectionError as exc:
        raise APIClientError(
            f"Cannot connect to FastAPI at {API_BASE_URL}. "
            "Start the backend and verify the port."
        ) from exc

    except requests.exceptions.Timeout as exc:
        raise APIClientError("Backend request timed out.") from exc

    except requests.exceptions.RequestException as exc:
        raise APIClientError(f"Network error: {exc}") from exc

    if not response.ok:
        raise APIClientError(
            f"Backend returned {response.status_code}: " f"{_response_error(response)}"
        )

    try:
        return response.json()

    except ValueError as exc:
        raise APIClientError("Backend returned a non-JSON response.") from exc


def api_post(
    endpoint: str,
    payload: Optional[Dict[str, Any]] = None,
    files=None,
    timeout: int = REQUEST_TIMEOUT,
) -> Any:
    try:
        if files is not None:
            response = requests.post(
                f"{API_BASE_URL}{endpoint}",
                files=files,
                timeout=timeout,
            )
        else:
            response = requests.post(
                f"{API_BASE_URL}{endpoint}",
                json=payload or {},
                timeout=timeout,
            )

    except requests.exceptions.ConnectionError as exc:
        raise APIClientError(f"Cannot connect to FastAPI at {API_BASE_URL}.") from exc

    except requests.exceptions.Timeout as exc:
        raise APIClientError("Backend request timed out.") from exc

    except requests.exceptions.RequestException as exc:
        raise APIClientError(f"Network error: {exc}") from exc

    if not response.ok:
        raise APIClientError(
            f"Backend returned {response.status_code}: " f"{_response_error(response)}"
        )

    try:
        return response.json()

    except ValueError:
        return {"message": response.text}


def api_post_first(
    endpoints: List[str],
    payload: Optional[Dict[str, Any]] = None,
) -> Any:
    last_error = None

    for endpoint in endpoints:
        try:
            return api_post(
                endpoint,
                payload=payload,
            )

        except APIClientError as exc:
            last_error = exc

            if "404" not in str(exc):
                raise

    raise last_error or APIClientError("No compatible endpoint was found.")


def extract_list(
    response: Any,
    keys: List[str],
) -> List[Dict[str, Any]]:
    if isinstance(response, list):
        return [as_dict(x) for x in response]

    if isinstance(response, dict):

        for key in keys:
            value = response.get(key)

            if isinstance(value, list):
                return [as_dict(x) for x in value]

        for key in ("data", "result"):
            value = response.get(key)

            if isinstance(value, list):
                return [as_dict(x) for x in value]

    return []


# ============================================================
# DATA LOADERS
# ============================================================


def load_payments() -> List[Dict[str, Any]]:
    response = api_get("/payments/")

    return extract_list(
        response,
        [
            "payments",
            "data",
            "results",
        ],
    )


def load_single_payment(
    payment_id: str,
) -> Dict[str, Any]:
    response = api_get(f"/payments/{payment_id}")

    if isinstance(response, dict):

        for key in (
            "payment",
            "payment_data",
            "data",
            "result",
        ):
            if isinstance(
                response.get(key),
                dict,
            ):
                return response[key]

        return response

    return {}


def load_validation_results() -> List[Dict[str, str]]:
    response = api_get("/validation/")

    return [
        normalize_validation(x)
        for x in extract_list(
            response,
            [
                "validation_results",
                "results",
                "data",
            ],
        )
    ]


def load_ai_rejections() -> List[Dict[str, str]]:
    response = api_get("/ai/rejections")

    return [
        normalize_ai(x)
        for x in extract_list(
            response,
            [
                "ai_rejections",
                "rejections",
                "results",
                "data",
            ],
        )
    ]


def load_audit_logs() -> List[Dict[str, str]]:
    response = api_get("/audit-logs/")

    return [
        normalize_audit(x)
        for x in extract_list(
            response,
            [
                "audit_logs",
                "logs",
                "results",
                "data",
            ],
        )
    ]


def load_optional(
    endpoint: str,
) -> Optional[Any]:
    try:
        return api_get(endpoint)

    except APIClientError as exc:
        if "404" in str(exc):
            return None

        raise


# ============================================================
# CACHE
# ============================================================


@st.cache_data(
    ttl=5,
    show_spinner=False,
)
def cached_payments():
    return load_payments()


@st.cache_data(
    ttl=5,
    show_spinner=False,
)
def cached_validation():
    return load_validation_results()


@st.cache_data(
    ttl=5,
    show_spinner=False,
)
def cached_ai():
    return load_ai_rejections()


@st.cache_data(
    ttl=5,
    show_spinner=False,
)
def cached_audit():
    return load_audit_logs()


def refresh_all():
    cached_payments.clear()
    cached_validation.clear()
    cached_ai.clear()
    cached_audit.clear()

    st.session_state.last_refresh = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    st.rerun()


# ============================================================
# SESSION STATE
# ============================================================

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

if "upload_result" not in st.session_state:
    st.session_state.upload_result = None

if "selected_payment_id" not in st.session_state:
    st.session_state.selected_payment_id = None


# ============================================================
# COMMON DATA
# ============================================================


def get_common_data():
    try:
        payments = cached_payments()

    except APIClientError as exc:
        payments = []
        st.error(f"Unable to load payments: {exc}")

    try:
        validations = cached_validation()

    except APIClientError as exc:
        validations = []
        st.error(f"Unable to load validation results: {exc}")

    try:
        ai_results = cached_ai()

    except APIClientError:
        ai_results = []

    return (
        payments,
        validations,
        ai_results,
    )


# ============================================================
# HEADER
# ============================================================

st.title("💳 PayFlow Intelligence")

st.subheader("Payment Operations & Data Quality Platform")

st.write(
    "Monitor payment processing, deterministic validation, "
    "AI rejection analysis, corrections, data lineage, "
    "analytics, and audit history."
)


# ============================================================
# NAVIGATION
# ============================================================

page = st.radio(
    "Navigation",
    [
        "Dashboard",
        "Upload Payments",
        "Payment Details",
        "Validation",
        "AI Analysis",
        "Analytics",
        "Audit Trail",
    ],
    horizontal=True,
    key="main_navigation",
)

st.divider()


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    col1, col2 = st.columns([5, 1])

    with col1:
        st.header("Payment Operations Dashboard")

        st.caption("Last refreshed: " + st.session_state.last_refresh)

    with col2:
        if st.button(
            "🔄 Refresh",
            use_container_width=True,
        ):
            refresh_all()

    # --------------------------------------------------------
    # BACKEND HEALTH
    # --------------------------------------------------------

    try:
        health = api_get(
            "/health",
            timeout=10,
        )

        health_status = safe_value(
            first_value(
                health,
                [
                    "status",
                    "health",
                    "state",
                ],
                "",
            )
        ).lower()

        if health_status in {
            "healthy",
            "success",
            "ok",
            "running",
        }:
            st.success("🟢 FastAPI Backend Connected")

        else:
            st.warning("🟡 Backend responded: " + (health_status or "unknown status"))

    except APIClientError as exc:
        st.error(f"🔴 Backend unavailable: {exc}")

    # --------------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------------

    payments, validations, ai_results = get_common_data()

    validation_map = {x["payment_id"]: x for x in validations if x.get("payment_id")}

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    total_payments = len(payments)

    valid_payments = sum(x["status"] == "VALID" for x in validations)

    rejected_payments = sum(x["status"] == "REJECTED" for x in validations)

    # IMPORTANT:
    # AI results do NOT automatically mean "Under Review".
    # Only pending/review states are counted.
    under_review = sum(
        x["status"]
        in {
            "PENDING",
            "UNDER_REVIEW",
        }
        for x in ai_results
    )

    success_rate = valid_payments / total_payments * 100 if total_payments else 0.0

    data_quality = success_rate

    # --------------------------------------------------------
    # PAYMENT OVERVIEW
    # --------------------------------------------------------

    st.subheader("Payment Overview")

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Total Payments",
        total_payments,
    )

    c2.metric(
        "Valid Payments",
        valid_payments,
    )

    c3.metric(
        "Rejected Payments",
        rejected_payments,
    )

    c4.metric(
        "Under Review",
        under_review,
    )

    c5.metric(
        "Success Rate",
        f"{success_rate:.1f}%",
    )

    st.divider()

    # --------------------------------------------------------
    # DATA QUALITY
    # --------------------------------------------------------

    q1, q2 = st.columns(2)

    with q1:
        st.subheader("Data Quality Score")

        st.progress(
            int(
                max(
                    0,
                    min(
                        100,
                        round(data_quality),
                    ),
                )
            )
        )

        st.metric(
            "Quality",
            f"{data_quality:.1f}%",
        )

    with q2:
        st.subheader("Review Queue")

        st.metric(
            "Items Needing Review",
            under_review,
        )

    st.divider()

    # --------------------------------------------------------
    # STATUS CHART
    # --------------------------------------------------------

    st.subheader("Payment Status Distribution")

    status_df = pd.DataFrame(
        {
            "Status": [
                "Valid",
                "Rejected",
                "Under Review",
            ],
            "Payments": [
                valid_payments,
                rejected_payments,
                under_review,
            ],
        }
    ).set_index("Status")

    st.bar_chart(status_df)

    st.divider()

    # --------------------------------------------------------
    # RECENT PAYMENTS
    # --------------------------------------------------------

    st.subheader("Recent Payments")

    rows = []

    for payment in payments:

        p = normalize_payment(payment)

        validation = validation_map.get(
            p["payment_id"],
            {},
        )

        rows.append(
            {
                "Payment ID": p["payment_id"],
                "Amount": p["amount"],
                "Currency": p["currency"],
                "Beneficiary": p["beneficiary"],
                "Status": validation.get(
                    "status",
                    "NOT_VALIDATED",
                ),
                "Rejection Reason": validation.get(
                    "errors",
                    "",
                ),
            }
        )

    if rows:

        st.dataframe(
            pd.DataFrame(rows).fillna("").astype(str),
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info("No payments are currently stored.")


# ============================================================
# UPLOAD PAYMENTS
# ============================================================

elif page == "Upload Payments":

    st.header("📤 Payment File Upload")

    st.write("Upload an XML, CSV, or JSON payment file " "for backend processing.")

    uploaded_file = st.file_uploader(
        "Choose payment file",
        type=[
            "xml",
            "csv",
            "json",
        ],
        help=(
            "The backend performs parsing, duplicate checks, "
            "validation, and persistence."
        ),
    )

    if uploaded_file is not None:

        c1, c2, c3 = st.columns(3)

        c1.write(f"**File:** {uploaded_file.name}")

        c2.write(f"**Type:** " f"{uploaded_file.type or 'unknown'}")

        c3.write(f"**Size:** " f"{uploaded_file.size:,} bytes")

        if st.button(
            "🚀 Process Payment File",
            type="primary",
            use_container_width=True,
        ):

            file_payload = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type or "application/octet-stream",
                )
            }

            with st.spinner("Uploading and processing payment file..."):

                try:

                    # Current backend endpoint.
                    try:
                        result = api_post(
                            "/upload/",
                            files=file_payload,
                            timeout=UPLOAD_TIMEOUT,
                        )

                    # Planned endpoint fallback.
                    except APIClientError as exc:

                        if "404" in str(exc):

                            result = api_post(
                                "/payments/upload",
                                files=file_payload,
                                timeout=UPLOAD_TIMEOUT,
                            )

                        else:
                            raise

                    st.session_state.upload_result = result

                    cached_payments.clear()
                    cached_validation.clear()
                    cached_ai.clear()
                    cached_audit.clear()

                    st.success("✅ Payment file processed successfully.")

                except APIClientError as exc:

                    st.error(f"❌ Processing failed: {exc}")

    # --------------------------------------------------------
    # UPLOAD RESULT
    # --------------------------------------------------------

    result = st.session_state.upload_result

    if result:

        st.divider()

        st.subheader("Processing Summary")

        total = first_value(
            result,
            [
                "total_payments",
                "count",
                "total",
            ],
            0,
        )

        valid = first_value(
            result,
            [
                "valid_payments",
                "accepted_payments",
                "valid",
            ],
            0,
        )

        invalid = first_value(
            result,
            [
                "invalid_payments",
                "rejected_payments",
                "rejected",
                "invalid",
            ],
            0,
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Total Payments",
            safe_value(total),
        )

        c2.metric(
            "Valid Payments",
            safe_value(valid),
        )

        c3.metric(
            "Rejected Payments",
            safe_value(invalid),
        )

        upload_validation = extract_list(
            result,
            [
                "validation_results",
                "results",
                "validations",
            ],
        )

        if upload_validation:

            st.divider()

            st.subheader("Validation Results")

            table = [normalize_validation(x) for x in upload_validation]

            st.dataframe(
                pd.DataFrame(table).fillna("").astype(str),
                use_container_width=True,
                hide_index=True,
            )


# ============================================================
# PAYMENT DETAILS
# ============================================================

elif page == "Payment Details":

    st.header("🔎 Payment Details")

    try:
        payments = cached_payments()

    except APIClientError as exc:

        payments = []

        st.error(f"Unable to load payments: {exc}")

    payment_ids = []

    for payment in payments:

        payment_id = normalize_payment(payment)["payment_id"]

        if payment_id:
            payment_ids.append(payment_id)

    if not payment_ids:

        st.info("No payments are currently stored.")

    else:

        if st.session_state.selected_payment_id in payment_ids:
            default_index = payment_ids.index(st.session_state.selected_payment_id)
        else:
            default_index = 0

        selected_id = st.selectbox(
            "Select Payment",
            payment_ids,
            index=default_index,
        )

        st.session_state.selected_payment_id = selected_id

        try:

            payment = load_single_payment(selected_id)

        except APIClientError:

            payment = next(
                (
                    p
                    for p in payments
                    if normalize_payment(p)["payment_id"] == selected_id
                ),
                {},
            )

        p = normalize_payment(payment)

        # ----------------------------------------------------
        # PAYMENT INFORMATION
        # ----------------------------------------------------

        st.subheader("Payment Information")

        a, b = st.columns(2)

        with a:

            st.text_input(
                "Payment ID",
                p["payment_id"],
                disabled=True,
            )

            st.text_input(
                "Amount",
                p["amount"],
                disabled=True,
            )

            st.text_input(
                "Debtor Name",
                p["debtor_name"],
                disabled=True,
            )

            st.text_input(
                "Debtor Account",
                p["debtor_account"],
                disabled=True,
            )

        with b:

            st.text_input(
                "Currency",
                p["currency"],
                disabled=True,
            )

            st.text_input(
                "Beneficiary",
                p["beneficiary"],
                disabled=True,
            )

            st.text_input(
                "Creditor Account",
                p["creditor_account"],
                disabled=True,
            )

            st.text_input(
                "Beneficiary Address",
                p["beneficiary_address"],
                disabled=True,
            )

        st.divider()

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        st.subheader("Validation / Rejection Details")

        try:
            validations = cached_validation()

        except APIClientError:
            validations = []

        selected_validation = next(
            (v for v in validations if v["payment_id"] == selected_id),
            None,
        )

        if not selected_validation:

            st.info("No validation result was found " "for this payment.")

        elif selected_validation["status"] == "VALID":

            st.success("✅ Payment passed validation.")

        else:

            st.error("❌ Payment failed validation.")

            if selected_validation["errors"]:

                st.write("**Validation Errors**")

                st.warning(selected_validation["errors"])

            if selected_validation["warnings"]:

                st.write("**Validation Warnings**")

                st.info(selected_validation["warnings"])

        st.divider()

        # ----------------------------------------------------
        # ORIGINAL / CURRENT DATA
        # ----------------------------------------------------

        st.subheader("Original vs Current Data")

        original = load_optional(f"/payments/{selected_id}/original")

        current = load_optional(f"/payments/{selected_id}/current")

        if original is None:

            original = (
                payment.get("original_data")
                if isinstance(
                    payment,
                    dict,
                )
                else None
            )

        if current is None:

            current = (
                payment.get("current_data")
                if isinstance(
                    payment,
                    dict,
                )
                else None
            )

        if isinstance(original, dict) or isinstance(current, dict):

            left, right = st.columns(2)

            with left:
                st.write("**Original Data**")
                st.json(original or {})

            with right:
                st.write("**Current Data**")
                st.json(current or {})

        else:

            st.info(
                "Original/current snapshots are not exposed " "by the current backend."
            )

        st.divider()

        # ----------------------------------------------------
        # CORRECTION HISTORY
        # ----------------------------------------------------

        st.subheader("Correction History")

        correction_response = load_optional(f"/payments/{selected_id}/corrections")

        correction_rows = (
            extract_list(
                correction_response,
                [
                    "corrections",
                    "history",
                    "data",
                    "results",
                ],
            )
            if correction_response is not None
            else []
        )

        if correction_rows:

            st.dataframe(
                pd.DataFrame(correction_rows).fillna("").astype(str),
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.info("No correction history is available " "for this payment.")

        st.divider()

        # ----------------------------------------------------
        # DATA LINEAGE
        # ----------------------------------------------------

        st.subheader("Data Lineage")

        lineage_response = load_optional(f"/payments/{selected_id}/lineage")

        lineage_rows = (
            extract_list(
                lineage_response,
                [
                    "lineage",
                    "data",
                    "results",
                ],
            )
            if lineage_response is not None
            else []
        )

        if lineage_rows:

            st.dataframe(
                pd.DataFrame(lineage_rows).fillna("").astype(str),
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.info("No field-level lineage is exposed " "by the current backend.")

        st.divider()

        # ----------------------------------------------------
        # PAYMENT AUDIT HISTORY
        # ----------------------------------------------------

        st.subheader("Payment Audit History")

        try:
            audit_logs = cached_audit()

        except APIClientError:
            audit_logs = []

        payment_logs = [x for x in audit_logs if x["payment_id"] == selected_id]

        if payment_logs:

            for log in payment_logs:

                with st.container(border=True):

                    st.write(
                        f"**{log['event_type']}** — "
                        f"{log['event_status']} — "
                        f"{log['created_at'] or 'time unavailable'}"
                    )

                    if log["description"]:

                        st.write(log["description"])

                    if log["details"]:

                        try:
                            st.json(json.loads(log["details"]))

                        except Exception:
                            st.code(log["details"])

        else:

            st.info("No audit history found " "for this payment.")


# ============================================================
# VALIDATION
# ============================================================

elif page == "Validation":

    st.header("✅ Payment Validation")

    st.write("Review deterministic validation results " "returned by FastAPI.")

    try:

        validation_results = cached_validation()

    except APIClientError as exc:

        validation_results = []

        st.error(f"Unable to retrieve validation results: {exc}")

    if not validation_results:

        st.info("No validation results are currently stored.")

    else:

        table = []

        for result in validation_results:

            table.append(
                {
                    "Payment ID": result["payment_id"],
                    "Status": result["status"],
                    "Errors": result["errors"],
                    "Warnings": result["warnings"],
                    "Created At": result["created_at"],
                }
            )

        st.dataframe(
            pd.DataFrame(table).fillna("").astype(str),
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        selected_id = st.selectbox(
            "Select Payment",
            [x["payment_id"] for x in validation_results],
        )

        selected = next(x for x in validation_results if x["payment_id"] == selected_id)

        if selected["status"] == "VALID":

            st.success("✅ Payment passed validation.")

        else:

            st.error("❌ Payment failed validation.")

        if selected["errors"]:

            st.write("**Validation Errors**")

            st.warning(selected["errors"])

        if selected["warnings"]:

            st.write("**Validation Warnings**")

            st.info(selected["warnings"])


# ============================================================
# AI ANALYSIS
# ============================================================

elif page == "AI Analysis":

    st.header("🤖 AI Rejection Analysis")

    st.write("Review rejection analysis generated " "by the local Ollama model.")

    try:

        ai_results = cached_ai()

    except APIClientError as exc:

        ai_results = []

        st.error(f"Unable to retrieve AI analysis: {exc}")

    if not ai_results:

        st.info("No AI rejection analysis is currently stored.")

        st.write(
            "Process a rejected payment through " "the Phase 10 Ollama workflow first."
        )

    else:

        st.success(f"{len(ai_results)} AI analysis " "result(s) found.")

        # ----------------------------------------------------
        # AI SUMMARY TABLE
        # ----------------------------------------------------

        ai_table = []

        for result in ai_results:

            ai_table.append(
                {
                    "Payment ID": result["payment_id"],
                    "Status": result["status"],
                    "Severity": result["severity"],
                    "Problematic Field": result["problematic_field"],
                    "Rejection Reason": result["rejection_reason"],
                }
            )

        st.dataframe(
            pd.DataFrame(ai_table).fillna("").astype(str),
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        ai_ids = [x["payment_id"] for x in ai_results if x["payment_id"]]

        if ai_ids:

            selected_id = st.selectbox(
                "Select Payment for AI Analysis",
                ai_ids,
            )

            selected_ai = next(x for x in ai_results if x["payment_id"] == selected_id)

            st.subheader("AI Rejection Analysis")

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Status",
                selected_ai["status"],
            )

            c2.metric(
                "Severity",
                selected_ai["severity"],
            )

            c3.metric(
                "Payment ID",
                selected_id,
            )

            if selected_ai["confidence"]:

                st.caption(
                    "AI confidence/review indicator: " + selected_ai["confidence"]
                )

            st.write("**Rejection Reason**")

            st.warning(selected_ai["rejection_reason"] or "Not available")

            st.write("**Root Cause**")

            st.info(selected_ai["root_cause"] or "Not available")

            st.write("**Problematic Field**")

            st.info(selected_ai["problematic_field"] or "Not available")

            st.write("**Recommendation / Suggested Correction**")

            st.success(selected_ai["recommendation"] or "Not available")

            st.write("**Explanation**")

            st.write(selected_ai["explanation"] or "Not available")

            # ------------------------------------------------
            # RAG ANALYSIS
            # ------------------------------------------------
            # Pass the complete deterministic validation result directly
            # to RAG. RAG must not reconstruct or hardcode an error.
            try:
                validation_results_for_rag = cached_validation()

                selected_validation_for_rag = next(
                    (
                        x
                        for x in validation_results_for_rag
                        if x.get("payment_id") == selected_id
                    ),
                    None,
                )

                if selected_validation_for_rag:
                    # RAG UI expects validation issues as a list.
                    # Backend/frontend normalization can return errors as a
                    # JSON string; passing that string directly makes Python
                    # iterate character-by-character (",", "c", "o", ...).
                    # Normalize it here without changing backend/RAG logic.
                    rag_validation_result = dict(selected_validation_for_rag)

                    for issue_key in ("errors", "warnings"):
                        raw_issues = rag_validation_result.get(issue_key, [])

                        if isinstance(raw_issues, str):
                            try:
                                parsed_issues = json.loads(raw_issues)
                            except (TypeError, ValueError, json.JSONDecodeError):
                                parsed_issues = None

                            if isinstance(parsed_issues, list):
                                raw_issues = parsed_issues
                            elif raw_issues.strip():
                                raw_issues = [raw_issues]
                            else:
                                raw_issues = []
                        elif raw_issues is None:
                            raw_issues = []
                        elif not isinstance(raw_issues, list):
                            raw_issues = [raw_issues]

                        rag_validation_result[issue_key] = raw_issues

                    st.divider()
                    show_rag_analysis(rag_validation_result)
                else:
                    st.info(
                        "No deterministic validation result is available "
                        "for RAG analysis."
                    )

            except Exception as exc:
                st.warning(f"RAG analysis unavailable: {exc}")

            st.divider()

            # ------------------------------------------------
            # HUMAN REVIEW
            # ------------------------------------------------

            st.subheader("Human Review")

            b1, b2 = st.columns(2)

            with b1:

                if st.button(
                    "✅ Approve Correction",
                    use_container_width=True,
                    type="primary",
                ):

                    try:

                        response = api_post_first(
                            [
                                (f"/payments/" f"{selected_id}/" "approve-correction"),
                                (f"/payments/" f"{selected_id}/approve"),
                            ],
                            payload={"payment_id": selected_id},
                        )

                        cached_payments.clear()
                        cached_validation.clear()
                        cached_ai.clear()
                        cached_audit.clear()

                        st.success("Correction approved.")

                        st.json(response)

                    except APIClientError as exc:

                        if "404" in str(exc):

                            st.warning(
                                "The backend does not expose "
                                "the correction approval endpoint yet."
                            )

                        else:

                            st.error(f"Approval failed: {exc}")

            with b2:

                if st.button(
                    "❌ Reject Suggestion",
                    use_container_width=True,
                ):

                    try:

                        response = api_post_first(
                            [
                                (f"/payments/" f"{selected_id}/" "reject-correction"),
                                (f"/payments/" f"{selected_id}/reject"),
                            ],
                            payload={"payment_id": selected_id},
                        )

                        cached_ai.clear()
                        cached_audit.clear()

                        st.success("AI correction suggestion rejected.")

                        st.json(response)

                    except APIClientError as exc:

                        if "404" in str(exc):

                            st.warning(
                                "The backend does not expose "
                                "the correction rejection endpoint yet."
                            )

                        else:

                            st.error(f"Rejection failed: {exc}")


# ============================================================
# ANALYTICS
# ============================================================

elif page == "Analytics":

    st.header("📊 Analytics")

    st.write("Operational and data-quality analytics " "derived from backend records.")

    payments, validations, ai_results = get_common_data()

    # --------------------------------------------------------
    # BACKEND ANALYTICS
    # --------------------------------------------------------

    try:

        analytics = load_optional("/analytics/summary")

    except APIClientError as exc:

        analytics = None

        st.warning(
            "Analytics endpoint unavailable. " "Using frontend aggregation instead."
        )

    if isinstance(
        analytics,
        dict,
    ):

        st.subheader("Backend Analytics Summary")

        metrics = {}

        for key, value in analytics.items():

            if isinstance(
                value,
                (str, int, float),
            ):

                metrics[
                    key.replace(
                        "_",
                        " ",
                    ).title()
                ] = value

        if metrics:

            cols = st.columns(
                min(
                    4,
                    len(metrics),
                )
            )

            for index, (
                key,
                value,
            ) in enumerate(metrics.items()):

                cols[index % len(cols)].metric(
                    key,
                    value,
                )

    st.divider()

    # --------------------------------------------------------
    # REJECTION BY REASON
    # --------------------------------------------------------

    reason_counts = {}

    for result in validations:

        if result["status"] == "REJECTED":

            reason = result["errors"] or "Unknown rejection reason"

            reason_counts[reason] = (
                reason_counts.get(
                    reason,
                    0,
                )
                + 1
            )

    st.subheader("Rejection Count by Reason")

    if reason_counts:

        df = pd.DataFrame(
            list(reason_counts.items()),
            columns=[
                "Reason",
                "Count",
            ],
        ).set_index("Reason")

        st.bar_chart(df)

    else:

        st.info("No rejected payments available " "for this chart.")

    # --------------------------------------------------------
    # CURRENCY DISTRIBUTION
    # --------------------------------------------------------

    currency_counts = {}

    for payment in payments:

        p = normalize_payment(payment)

        currency = p["currency"] or "UNKNOWN"

        currency_counts[currency] = (
            currency_counts.get(
                currency,
                0,
            )
            + 1
        )

    st.subheader("Payment Count by Currency")

    if currency_counts:

        df = pd.DataFrame(
            list(currency_counts.items()),
            columns=[
                "Currency",
                "Payments",
            ],
        ).set_index("Currency")

        st.bar_chart(df)

    else:

        st.info("No currency data available.")

    # --------------------------------------------------------
    # AI SEVERITY
    # --------------------------------------------------------

    severity_counts = {}

    for result in ai_results:

        severity = result["severity"] or "UNKNOWN"

        severity_counts[severity] = (
            severity_counts.get(
                severity,
                0,
            )
            + 1
        )

    st.subheader("AI Rejection Severity")

    if severity_counts:

        df = pd.DataFrame(
            list(severity_counts.items()),
            columns=[
                "Severity",
                "Payments",
            ],
        ).set_index("Severity")

        st.bar_chart(df)

    else:

        st.info("No AI severity data available.")


# ============================================================
# AUDIT TRAIL
# ============================================================

elif page == "Audit Trail":

    st.header("📜 Audit Trail")

    st.write(
        "Track payment processing events, validation, "
        "AI analysis, corrections, and data-lineage events."
    )

    if st.button("🔄 Refresh Audit Trail"):

        cached_audit.clear()

        refresh_all()

    try:

        audit_logs = cached_audit()

    except APIClientError as exc:

        audit_logs = []

        st.error(f"❌ Unable to retrieve audit logs: {exc}")

    total_events = len(audit_logs)

    successful_events = sum(
        x["event_status"]
        in {
            "SUCCESS",
            "COMPLETED",
            "VALID",
        }
        for x in audit_logs
    )

    failed_events = sum(
        x["event_status"]
        in {
            "FAILED",
            "ERROR",
            "REJECTED",
        }
        for x in audit_logs
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Total Audit Events",
        total_events,
    )

    c2.metric(
        "Successful Events",
        successful_events,
    )

    c3.metric(
        "Failed Events",
        failed_events,
    )

    st.divider()

    if not audit_logs:

        st.info(
            "No audit events found yet. " "Upload and process a payment file first."
        )

    else:

        st.subheader("Processing History")

        event_types = sorted({x["event_type"] or "UNKNOWN" for x in audit_logs})

        selected_event = st.selectbox(
            "Filter by Event Type",
            ["All"] + event_types,
        )

        filtered = [
            x
            for x in audit_logs
            if (selected_event == "All" or x["event_type"] == selected_event)
        ]

        st.write(
            f"Showing **{len(filtered)}** " f"of **{len(audit_logs)}** audit events"
        )

        audit_table = [
            {
                "Event": x["event_type"],
                "Status": x["event_status"],
                "Payment ID": x["payment_id"],
                "Description": x["description"],
                "Created At": x["created_at"],
            }
            for x in filtered
        ]

        st.dataframe(
            pd.DataFrame(audit_table).fillna("").astype(str),
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader("Detailed Audit Events")

        for log in filtered:

            label = (
                f"{log['event_type']} — "
                f"{log['event_status']} — "
                f"{log['payment_id'] or 'File-level event'}"
            )

            with st.expander(label):

                a, b = st.columns(2)

                with a:

                    st.write("**Event Type**")

                    st.write(log["event_type"])

                    st.write("**Event Status**")

                    st.write(log["event_status"])

                with b:

                    st.write("**Payment ID**")

                    st.write(log["payment_id"] or "-")

                    st.write("**Created At**")

                    st.write(log["created_at"] or "-")

                if log["description"]:

                    st.write("**Description**")

                    st.write(log["description"])

                if log["details"]:

                    st.write("**Details**")

                    try:

                        st.json(json.loads(log["details"]))

                    except Exception:

                        st.code(log["details"])


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption("PayFlow Intelligence • Streamlit frontend • " f"FastAPI: {API_BASE_URL}")
