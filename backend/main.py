# import json
# import os
# from datetime import datetime
# from typing import Any, Dict, List, Optional
# from rag.rag_ui import show_rag_analysis

# import pandas as pd
# import requests
# import streamlit as st

# # ============================================================
# # CONFIGURATION
# # ============================================================

# API_BASE_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8000").rstrip("/")
# REQUEST_TIMEOUT = int(os.getenv("FASTAPI_TIMEOUT", "30"))
# UPLOAD_TIMEOUT = int(os.getenv("FASTAPI_UPLOAD_TIMEOUT", "180"))


# # ============================================================
# # PAGE CONFIGURATION
# # ============================================================

# st.set_page_config(
#     page_title="PayFlow Intelligence",
#     page_icon="💳",
#     layout="wide",
#     initial_sidebar_state="collapsed",
# )


# # ============================================================
# # LIGHT UI STYLING
# # ============================================================

# st.markdown(
#     """
#     <style>
#         .block-container {
#             padding-top: 2rem;
#             padding-bottom: 3rem;
#         }
#         .small-muted {
#             color: #8b8f98;
#             font-size: 0.9rem;
#         }

#         /* Keep Streamlit alert text readable on light alert backgrounds. */
#         [data-testid="stAlert"] p,
#         [data-testid="stAlert"] div,
#         [data-testid="stAlert"] span {
#             color: #1f2937 !important;
#         }

#         /* Improve dataframe readability and prevent narrow columns. */
#         [data-testid="stDataFrame"] {
#             width: 100%;
#         }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )


# # ============================================================
# # CUSTOM ERROR
# # ============================================================


# class APIClientError(Exception):
#     pass


# # ============================================================
# # SAFE / NORMALIZATION HELPERS
# # ============================================================

# MISSING = object()


# def safe_value(value: Any, default: str = "") -> str:
#     """Convert backend values into safe Streamlit display values."""
#     if value is None:
#         return default

#     if isinstance(value, (list, tuple, set)):
#         return ", ".join(safe_value(v) for v in value)

#     if isinstance(value, dict):
#         try:
#             return json.dumps(value, ensure_ascii=False, default=str)
#         except Exception:
#             return str(value)

#     return str(value)


# def as_dict(value: Any) -> Dict[str, Any]:
#     return value if isinstance(value, dict) else {}


# def first_value(
#     data: Dict[str, Any],
#     keys: List[str],
#     default: Any = "",
# ) -> Any:
#     """
#     Look for a field in the object and common backend wrappers.

#     This prevents the UI from showing blank values when the backend
#     wraps data inside payment/payment_data/data/details objects.
#     """
#     if not isinstance(data, dict):
#         return default

#     containers = [data]

#     for wrapper in (
#         "payment",
#         "payment_data",
#         "data",
#         "details",
#         "original_data",
#         "current_data",
#     ):
#         value = data.get(wrapper)
#         if isinstance(value, dict):
#             containers.append(value)

#     for container in containers:
#         for key in keys:
#             value = container.get(key, MISSING)

#             if value is not MISSING and value not in (None, ""):
#                 return value

#     return default


# def person_name(value: Any) -> str:
#     """
#     Handle beneficiary/debtor values that may be either a string
#     or a nested object.
#     """
#     if isinstance(value, dict):
#         for key in (
#             "name",
#             "full_name",
#             "beneficiary_name",
#             "creditor_name",
#             "debtor_name",
#             "display_name",
#         ):
#             if value.get(key):
#                 return safe_value(value[key])

#         return safe_value(value)

#     return safe_value(value)


# def normalize_status(value: Any) -> str:
#     status = safe_value(value, "UNKNOWN").strip().upper()

#     aliases = {
#         "VALID": "VALID",
#         "ACCEPTED": "VALID",
#         "SUCCESS": "VALID",
#         "COMPLETED": "VALID",
#         "INVALID": "REJECTED",
#         "FAILED": "REJECTED",
#         "FAILURE": "REJECTED",
#         "REJECTED": "REJECTED",
#         "PENDING": "PENDING",
#         "UNDER REVIEW": "UNDER_REVIEW",
#         "UNDER_REVIEW": "UNDER_REVIEW",
#         "IN_REVIEW": "UNDER_REVIEW",
#     }

#     return aliases.get(status, status or "UNKNOWN")


# def normalize_payment(payment: Dict[str, Any]) -> Dict[str, str]:
#     beneficiary = first_value(
#         payment,
#         [
#             "beneficiary",
#             "beneficiary_name",
#             "creditor_name",
#             "creditor",
#             "payee_name",
#         ],
#     )

#     debtor = first_value(
#         payment,
#         [
#             "debtor_name",
#             "debtor",
#             "payer_name",
#             "originator_name",
#         ],
#     )

#     return {
#         "payment_id": safe_value(
#             first_value(
#                 payment,
#                 ["payment_id", "instruction_id", "instr_id", "id"],
#             )
#         ),
#         "amount": safe_value(
#             first_value(
#                 payment,
#                 ["amount", "instructed_amount", "payment_amount"],
#             )
#         ),
#         "currency": safe_value(
#             first_value(
#                 payment,
#                 ["currency", "currency_code", "ccy"],
#             )
#         ),
#         "beneficiary": person_name(beneficiary),
#         "debtor_name": person_name(debtor),
#         "debtor_account": safe_value(
#             first_value(
#                 payment,
#                 [
#                     "debtor_account",
#                     "debtor_iban",
#                     "payer_account",
#                 ],
#             )
#         ),
#         "creditor_account": safe_value(
#             first_value(
#                 payment,
#                 [
#                     "creditor_account",
#                     "creditor_iban",
#                     "beneficiary_account",
#                 ],
#             )
#         ),
#         "beneficiary_address": safe_value(
#             first_value(
#                 payment,
#                 [
#                     "beneficiary_address",
#                     "creditor_address",
#                     "payee_address",
#                 ],
#             )
#         ),
#         "created_at": safe_value(
#             first_value(
#                 payment,
#                 ["created_at", "timestamp", "created"],
#             )
#         ),
#     }


# def normalize_validation(result: Dict[str, Any]) -> Dict[str, str]:
#     result = as_dict(result)

#     errors = result.get("errors")

#     if errors is None:
#         errors = result.get("validation_errors")

#     if errors is None:
#         errors = result.get("validation_message", "")

#     warnings = result.get("warnings")

#     if warnings is None:
#         warnings = result.get("validation_warnings", "")

#     return {
#         "payment_id": safe_value(
#             first_value(
#                 result,
#                 ["payment_id", "instruction_id", "id"],
#             )
#         ),
#         "status": normalize_status(
#             first_value(
#                 result,
#                 ["status", "validation_status", "result"],
#             )
#         ),
#         "errors": safe_value(errors),
#         "warnings": safe_value(warnings),
#         "created_at": safe_value(
#             first_value(
#                 result,
#                 ["created_at", "timestamp", "created"],
#             )
#         ),
#     }


# def parse_issue_items(value: Any) -> List[Dict[str, Any]]:
#     """Normalize validation errors/warnings into a list of dictionaries."""
#     if value is None or value == "":
#         return []

#     if isinstance(value, dict):
#         return [value]

#     if isinstance(value, list):
#         return [item for item in value if isinstance(item, dict)]

#     if isinstance(value, str):
#         text = value.strip()
#         if not text:
#             return []

#         try:
#             parsed = json.loads(text)
#             if isinstance(parsed, dict):
#                 return [parsed]
#             if isinstance(parsed, list):
#                 return [item for item in parsed if isinstance(item, dict)]
#         except Exception:
#             return []

#     return []


# def issue_codes(value: Any) -> str:
#     """Return compact validation codes for table display."""
#     items = parse_issue_items(value)
#     codes = []

#     for item in items:
#         code = safe_value(item.get("code", "")).strip()
#         if code and code not in codes:
#             codes.append(code)

#     if codes:
#         return "\n".join(codes)

#     text = safe_value(value).strip()
#     return text if text else "—"


# def issue_details(value: Any) -> List[Dict[str, str]]:
#     """Return clean field/code/message details for expanded views."""
#     items = parse_issue_items(value)
#     details = []

#     for item in items:
#         details.append(
#             {
#                 "Field": safe_value(item.get("field"), "—"),
#                 "Code": safe_value(item.get("code"), "—"),
#                 "Message": safe_value(item.get("message"), "—"),
#             }
#         )

#     if details:
#         return details

#     text = safe_value(value).strip()
#     if text:
#         return [{"Field": "—", "Code": "—", "Message": text}]

#     return []


# def validation_table_config():
#     """Consistent column sizing for validation tables."""
#     return {
#         "Payment ID": st.column_config.TextColumn("Payment ID", width="medium"),
#         "Status": st.column_config.TextColumn("Status", width="small"),
#         "Errors": st.column_config.TextColumn(
#             "Errors", width="large", help="Validation error codes"
#         ),
#         "Warnings": st.column_config.TextColumn(
#             "Warnings", width="large", help="Validation warning codes"
#         ),
#         "Created At": st.column_config.TextColumn("Created At", width="medium"),
#     }


# def render_issue_details(title: str, value: Any, kind: str = "error"):
#     """Render full validation details without clipping or raw JSON."""
#     details = issue_details(value)
#     if not details:
#         return

#     st.write(f"**{title}**")
#     df = pd.DataFrame(details)

#     st.dataframe(
#         df,
#         use_container_width=True,
#         hide_index=True,
#         height=min(260, 65 + (len(df) * 55)),
#         column_config={
#             "Field": st.column_config.TextColumn("Field", width="medium"),
#             "Code": st.column_config.TextColumn("Code", width="medium"),
#             "Message": st.column_config.TextColumn("Message", width="large"),
#         },
#     )


# def normalize_ai(result: Dict[str, Any]) -> Dict[str, str]:
#     result = as_dict(result)

#     return {
#         "payment_id": safe_value(
#             first_value(
#                 result,
#                 ["payment_id", "instruction_id", "id"],
#             )
#         ),
#         "status": normalize_status(
#             first_value(
#                 result,
#                 ["status", "ai_status", "analysis_status"],
#             )
#         ),
#         "severity": safe_value(
#             first_value(
#                 result,
#                 ["severity", "ai_severity"],
#                 "UNKNOWN",
#             )
#         ).upper(),
#         "rejection_reason": safe_value(
#             first_value(
#                 result,
#                 [
#                     "rejection_reason",
#                     "ai_rejection_reason",
#                     "reason",
#                 ],
#             )
#         ),
#         "root_cause": safe_value(
#             first_value(
#                 result,
#                 ["root_cause", "ai_root_cause"],
#             )
#         ),
#         "problematic_field": safe_value(
#             first_value(
#                 result,
#                 [
#                     "problematic_field",
#                     "ai_problematic_field",
#                     "field",
#                 ],
#             )
#         ),
#         "recommendation": safe_value(
#             first_value(
#                 result,
#                 [
#                     "recommendation",
#                     "ai_recommendation",
#                     "suggested_correction",
#                 ],
#             )
#         ),
#         "explanation": safe_value(
#             first_value(
#                 result,
#                 [
#                     "explanation",
#                     "ai_explanation",
#                     "analysis",
#                 ],
#             )
#         ),
#         "confidence": safe_value(
#             first_value(
#                 result,
#                 [
#                     "confidence",
#                     "ai_confidence",
#                     "confidence_score",
#                 ],
#             )
#         ),
#     }


# def normalize_audit(log: Dict[str, Any]) -> Dict[str, str]:
#     log = as_dict(log)

#     return {
#         "event_type": safe_value(
#             first_value(
#                 log,
#                 [
#                     "event_type",
#                     "event",
#                     "type",
#                     "action",
#                 ],
#                 "UNKNOWN",
#             )
#         ).upper(),
#         "event_status": safe_value(
#             first_value(
#                 log,
#                 [
#                     "event_status",
#                     "status",
#                     "result",
#                 ],
#                 "UNKNOWN",
#             )
#         ).upper(),
#         "payment_id": safe_value(
#             first_value(
#                 log,
#                 [
#                     "payment_id",
#                     "instruction_id",
#                     "id",
#                 ],
#                 "-",
#             )
#         ),
#         "description": safe_value(
#             first_value(
#                 log,
#                 [
#                     "description",
#                     "message",
#                     "details_summary",
#                 ],
#                 "",
#             )
#         ),
#         "details": safe_value(
#             first_value(
#                 log,
#                 [
#                     "details",
#                     "metadata",
#                     "payload",
#                 ],
#                 "",
#             )
#         ),
#         "created_at": safe_value(
#             first_value(
#                 log,
#                 [
#                     "created_at",
#                     "timestamp",
#                     "created",
#                     "time",
#                 ],
#                 "",
#             )
#         ),
#     }


# # ============================================================
# # API CLIENT
# # ============================================================


# def _response_error(response: requests.Response) -> str:
#     try:
#         payload = response.json()

#         if isinstance(payload, dict):
#             detail = (
#                 payload.get("detail") or payload.get("message") or payload.get("error")
#             )

#             if detail:
#                 return safe_value(detail)

#     except Exception:
#         pass

#     return response.text[:1000] or "Unknown backend error."


# def api_get(
#     endpoint: str,
#     timeout: int = REQUEST_TIMEOUT,
# ) -> Any:
#     try:
#         response = requests.get(
#             f"{API_BASE_URL}{endpoint}",
#             timeout=timeout,
#         )

#     except requests.exceptions.ConnectionError as exc:
#         raise APIClientError(
#             f"Cannot connect to FastAPI at {API_BASE_URL}. "
#             "Start the backend and verify the port."
#         ) from exc

#     except requests.exceptions.Timeout as exc:
#         raise APIClientError("Backend request timed out.") from exc

#     except requests.exceptions.RequestException as exc:
#         raise APIClientError(f"Network error: {exc}") from exc

#     if not response.ok:
#         raise APIClientError(
#             f"Backend returned {response.status_code}: " f"{_response_error(response)}"
#         )

#     try:
#         return response.json()

#     except ValueError as exc:
#         raise APIClientError("Backend returned a non-JSON response.") from exc


# def api_post(
#     endpoint: str,
#     payload: Optional[Dict[str, Any]] = None,
#     files=None,
#     timeout: int = REQUEST_TIMEOUT,
# ) -> Any:
#     try:
#         if files is not None:
#             response = requests.post(
#                 f"{API_BASE_URL}{endpoint}",
#                 files=files,
#                 timeout=timeout,
#             )
#         else:
#             response = requests.post(
#                 f"{API_BASE_URL}{endpoint}",
#                 json=payload or {},
#                 timeout=timeout,
#             )

#     except requests.exceptions.ConnectionError as exc:
#         raise APIClientError(f"Cannot connect to FastAPI at {API_BASE_URL}.") from exc

#     except requests.exceptions.Timeout as exc:
#         raise APIClientError("Backend request timed out.") from exc

#     except requests.exceptions.RequestException as exc:
#         raise APIClientError(f"Network error: {exc}") from exc

#     if not response.ok:
#         raise APIClientError(
#             f"Backend returned {response.status_code}: " f"{_response_error(response)}"
#         )

#     try:
#         return response.json()

#     except ValueError:
#         return {"message": response.text}


# def api_post_first(
#     endpoints: List[str],
#     payload: Optional[Dict[str, Any]] = None,
# ) -> Any:
#     last_error = None

#     for endpoint in endpoints:
#         try:
#             return api_post(
#                 endpoint,
#                 payload=payload,
#             )

#         except APIClientError as exc:
#             last_error = exc

#             if "404" not in str(exc):
#                 raise

#     raise last_error or APIClientError("No compatible endpoint was found.")


# def extract_list(
#     response: Any,
#     keys: List[str],
# ) -> List[Dict[str, Any]]:
#     if isinstance(response, list):
#         return [as_dict(x) for x in response]

#     if isinstance(response, dict):

#         for key in keys:
#             value = response.get(key)

#             if isinstance(value, list):
#                 return [as_dict(x) for x in value]

#         for key in ("data", "result"):
#             value = response.get(key)

#             if isinstance(value, list):
#                 return [as_dict(x) for x in value]

#     return []


# # ============================================================
# # DATA LOADERS
# # ============================================================


# def load_payments() -> List[Dict[str, Any]]:
#     response = api_get("/payments/")

#     return extract_list(
#         response,
#         [
#             "payments",
#             "data",
#             "results",
#         ],
#     )


# def load_single_payment(
#     payment_id: str,
# ) -> Dict[str, Any]:
#     response = api_get(f"/payments/{payment_id}")

#     if isinstance(response, dict):

#         for key in (
#             "payment",
#             "payment_data",
#             "data",
#             "result",
#         ):
#             if isinstance(
#                 response.get(key),
#                 dict,
#             ):
#                 return response[key]

#         return response

#     return {}


# def load_validation_results() -> List[Dict[str, str]]:
#     response = api_get("/validation/")

#     return [
#         normalize_validation(x)
#         for x in extract_list(
#             response,
#             [
#                 "validation_results",
#                 "results",
#                 "data",
#             ],
#         )
#     ]


# def load_ai_rejections() -> List[Dict[str, str]]:
#     response = api_get("/ai/rejections")

#     return [
#         normalize_ai(x)
#         for x in extract_list(
#             response,
#             [
#                 "ai_rejections",
#                 "rejections",
#                 "results",
#                 "data",
#             ],
#         )
#     ]


# def load_audit_logs() -> List[Dict[str, str]]:
#     response = api_get("/audit-logs/")

#     return [
#         normalize_audit(x)
#         for x in extract_list(
#             response,
#             [
#                 "audit_logs",
#                 "logs",
#                 "results",
#                 "data",
#             ],
#         )
#     ]


# def load_optional(
#     endpoint: str,
# ) -> Optional[Any]:
#     try:
#         return api_get(endpoint)

#     except APIClientError as exc:
#         if "404" in str(exc):
#             return None

#         raise


# # ============================================================
# # CACHE
# # ============================================================


# @st.cache_data(
#     ttl=5,
#     show_spinner=False,
# )
# def cached_payments():
#     return load_payments()


# @st.cache_data(
#     ttl=5,
#     show_spinner=False,
# )
# def cached_validation():
#     return load_validation_results()


# @st.cache_data(
#     ttl=5,
#     show_spinner=False,
# )
# def cached_ai():
#     return load_ai_rejections()


# @st.cache_data(
#     ttl=5,
#     show_spinner=False,
# )
# def cached_audit():
#     return load_audit_logs()


# def refresh_all():
#     cached_payments.clear()
#     cached_validation.clear()
#     cached_ai.clear()
#     cached_audit.clear()

#     st.session_state.last_refresh = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

#     st.rerun()


# # ============================================================
# # SESSION STATE
# # ============================================================

# if "last_refresh" not in st.session_state:
#     st.session_state.last_refresh = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

# if "upload_result" not in st.session_state:
#     st.session_state.upload_result = None

# if "selected_payment_id" not in st.session_state:
#     st.session_state.selected_payment_id = None


# # ============================================================
# # COMMON DATA
# # ============================================================


# def get_common_data():
#     try:
#         payments = cached_payments()

#     except APIClientError as exc:
#         payments = []
#         st.error(f"Unable to load payments: {exc}")

#     try:
#         validations = cached_validation()

#     except APIClientError as exc:
#         validations = []
#         st.error(f"Unable to load validation results: {exc}")

#     try:
#         ai_results = cached_ai()

#     except APIClientError:
#         ai_results = []

#     return (
#         payments,
#         validations,
#         ai_results,
#     )


# # ============================================================
# # HEADER
# # ============================================================

# st.title("💳 PayFlow Intelligence")

# st.subheader("Payment Operations & Data Quality Platform")

# st.write(
#     "Monitor payment processing, deterministic validation, "
#     "AI rejection analysis, corrections, data lineage, "
#     "analytics, and audit history."
# )


# # ============================================================
# # NAVIGATION
# # ============================================================

# page = st.radio(
#     "Navigation",
#     [
#         "Dashboard",
#         "Upload Payments",
#         "Payment Details",
#         "Validation",
#         "AI Analysis",
#         "Analytics",
#         "Audit Trail",
#     ],
#     horizontal=True,
#     key="main_navigation",
# )

# st.divider()


# # ============================================================
# # DASHBOARD
# # ============================================================

# if page == "Dashboard":

#     col1, col2 = st.columns([5, 1])

#     with col1:
#         st.header("Payment Operations Dashboard")

#         st.caption("Last refreshed: " + st.session_state.last_refresh)

#     with col2:
#         if st.button(
#             "🔄 Refresh",
#             use_container_width=True,
#         ):
#             refresh_all()

#     # --------------------------------------------------------
#     # BACKEND HEALTH
#     # --------------------------------------------------------

#     try:
#         health = api_get(
#             "/health",
#             timeout=10,
#         )

#         health_status = safe_value(
#             first_value(
#                 health,
#                 [
#                     "status",
#                     "health",
#                     "state",
#                 ],
#                 "",
#             )
#         ).lower()

#         if health_status in {
#             "healthy",
#             "success",
#             "ok",
#             "running",
#         }:
#             st.success("🟢 FastAPI Backend Connected")

#         else:
#             st.warning("🟡 Backend responded: " + (health_status or "unknown status"))

#     except APIClientError as exc:
#         st.error(f"🔴 Backend unavailable: {exc}")

#     # --------------------------------------------------------
#     # LOAD DATA
#     # --------------------------------------------------------

#     payments, validations, ai_results = get_common_data()

#     validation_map = {x["payment_id"]: x for x in validations if x.get("payment_id")}

#     # --------------------------------------------------------
#     # METRICS
#     # --------------------------------------------------------

#     total_payments = len(payments)

#     valid_payments = sum(x["status"] == "VALID" for x in validations)

#     rejected_payments = sum(x["status"] == "REJECTED" for x in validations)

#     # IMPORTANT:
#     # AI results do NOT automatically mean "Under Review".
#     # Only pending/review states are counted.
#     under_review = sum(
#         x["status"]
#         in {
#             "PENDING",
#             "UNDER_REVIEW",
#         }
#         for x in ai_results
#     )

#     success_rate = valid_payments / total_payments * 100 if total_payments else 0.0

#     data_quality = success_rate

#     # --------------------------------------------------------
#     # PAYMENT OVERVIEW
#     # --------------------------------------------------------

#     st.subheader("Payment Overview")

#     c1, c2, c3, c4, c5 = st.columns(5)

#     c1.metric(
#         "Total Payments",
#         total_payments,
#     )

#     c2.metric(
#         "Valid Payments",
#         valid_payments,
#     )

#     c3.metric(
#         "Rejected Payments",
#         rejected_payments,
#     )

#     c4.metric(
#         "Under Review",
#         under_review,
#     )

#     c5.metric(
#         "Success Rate",
#         f"{success_rate:.1f}%",
#     )

#     st.divider()

#     # --------------------------------------------------------
#     # DATA QUALITY
#     # --------------------------------------------------------

#     q1, q2 = st.columns(2)

#     with q1:
#         st.subheader("Data Quality Score")

#         st.progress(
#             int(
#                 max(
#                     0,
#                     min(
#                         100,
#                         round(data_quality),
#                     ),
#                 )
#             )
#         )

#         st.metric(
#             "Quality",
#             f"{data_quality:.1f}%",
#         )

#     with q2:
#         st.subheader("Review Queue")

#         st.metric(
#             "Items Needing Review",
#             under_review,
#         )

#     st.divider()

#     # --------------------------------------------------------
#     # STATUS CHART
#     # --------------------------------------------------------

#     st.subheader("Payment Status Distribution")

#     status_df = pd.DataFrame(
#         {
#             "Status": [
#                 "Valid",
#                 "Rejected",
#                 "Under Review",
#             ],
#             "Payments": [
#                 valid_payments,
#                 rejected_payments,
#                 under_review,
#             ],
#         }
#     ).set_index("Status")

#     st.bar_chart(status_df)

#     st.divider()

#     # --------------------------------------------------------
#     # RECENT PAYMENTS
#     # --------------------------------------------------------

#     st.subheader("Recent Payments")

#     rows = []

#     for payment in payments:

#         p = normalize_payment(payment)

#         validation = validation_map.get(
#             p["payment_id"],
#             {},
#         )

#         rows.append(
#             {
#                 "Payment ID": p["payment_id"],
#                 "Amount": p["amount"],
#                 "Currency": p["currency"],
#                 "Beneficiary": p["beneficiary"],
#                 "Status": validation.get(
#                     "status",
#                     "NOT_VALIDATED",
#                 ),
#                 "Rejection Reason": issue_codes(validation.get("errors", "")),
#             }
#         )

#     if rows:

#         recent_df = pd.DataFrame(rows).fillna("").astype(str)
#         if "Rejection Reason" in recent_df.columns:
#             recent_df["Rejection Reason"] = recent_df["Rejection Reason"].apply(
#                 issue_codes
#             )

#         st.dataframe(
#             recent_df,
#             use_container_width=True,
#             hide_index=True,
#             row_height=52,
#             column_config={
#                 "Payment ID": st.column_config.TextColumn("Payment ID", width="medium"),
#                 "Amount": st.column_config.TextColumn("Amount", width="medium"),
#                 "Currency": st.column_config.TextColumn("Currency", width="small"),
#                 "Beneficiary": st.column_config.TextColumn(
#                     "Beneficiary", width="large"
#                 ),
#                 "Status": st.column_config.TextColumn("Status", width="small"),
#                 "Rejection Reason": st.column_config.TextColumn(
#                     "Rejection Reason", width="large"
#                 ),
#             },
#         )

#     else:
#         st.info("No payments are currently stored.")


# # ============================================================
# # UPLOAD PAYMENTS
# # ============================================================

# elif page == "Upload Payments":

#     st.header("📤 Payment File Upload")

#     st.write("Upload an XML, CSV, or JSON payment file " "for backend processing.")

#     uploaded_file = st.file_uploader(
#         "Choose payment file",
#         type=[
#             "xml",
#             "csv",
#             "json",
#         ],
#         help=(
#             "The backend performs parsing, duplicate checks, "
#             "validation, and persistence."
#         ),
#     )

#     if uploaded_file is not None:

#         c1, c2, c3 = st.columns(3)

#         c1.write(f"**File:** {uploaded_file.name}")

#         c2.write(f"**Type:** " f"{uploaded_file.type or 'unknown'}")

#         c3.write(f"**Size:** " f"{uploaded_file.size:,} bytes")

#         if st.button(
#             "🚀 Process Payment File",
#             type="primary",
#             use_container_width=True,
#         ):

#             file_payload = {
#                 "file": (
#                     uploaded_file.name,
#                     uploaded_file.getvalue(),
#                     uploaded_file.type or "application/octet-stream",
#                 )
#             }

#             with st.spinner("Uploading and processing payment file..."):

#                 try:

#                     # Current backend endpoint.
#                     try:
#                         result = api_post(
#                             "/upload/",
#                             files=file_payload,
#                             timeout=UPLOAD_TIMEOUT,
#                         )

#                     # Planned endpoint fallback.
#                     except APIClientError as exc:

#                         if "404" in str(exc):

#                             result = api_post(
#                                 "/payments/upload",
#                                 files=file_payload,
#                                 timeout=UPLOAD_TIMEOUT,
#                             )

#                         else:
#                             raise

#                     st.session_state.upload_result = result

#                     cached_payments.clear()
#                     cached_validation.clear()
#                     cached_ai.clear()
#                     cached_audit.clear()

#                     st.success("✅ Payment file processed successfully.")

#                 except APIClientError as exc:

#                     st.error(f"❌ Processing failed: {exc}")

#     # --------------------------------------------------------
#     # UPLOAD RESULT
#     # --------------------------------------------------------

#     result = st.session_state.upload_result

#     if result:

#         st.divider()

#         st.subheader("Processing Summary")

#         total = first_value(
#             result,
#             [
#                 "total_payments",
#                 "count",
#                 "total",
#             ],
#             0,
#         )

#         valid = first_value(
#             result,
#             [
#                 "valid_payments",
#                 "accepted_payments",
#                 "valid",
#             ],
#             0,
#         )

#         invalid = first_value(
#             result,
#             [
#                 "invalid_payments",
#                 "rejected_payments",
#                 "rejected",
#                 "invalid",
#             ],
#             0,
#         )

#         c1, c2, c3 = st.columns(3)

#         c1.metric(
#             "Total Payments",
#             safe_value(total),
#         )

#         c2.metric(
#             "Valid Payments",
#             safe_value(valid),
#         )

#         c3.metric(
#             "Rejected Payments",
#             safe_value(invalid),
#         )

#         upload_validation = extract_list(
#             result,
#             [
#                 "validation_results",
#                 "results",
#                 "validations",
#             ],
#         )

#         if upload_validation:

#             st.divider()

#             st.subheader("Validation Results")

#             table = [normalize_validation(x) for x in upload_validation]

#             upload_df = pd.DataFrame(table).fillna("").astype(str)

#             # Compact issue codes keep upload results readable.
#             if "Errors" in upload_df.columns:
#                 upload_df["Errors"] = upload_df["Errors"].apply(issue_codes)
#             if "Warnings" in upload_df.columns:
#                 upload_df["Warnings"] = upload_df["Warnings"].apply(issue_codes)

#             st.dataframe(
#                 upload_df,
#                 use_container_width=True,
#                 hide_index=True,
#                 row_height=52,
#                 column_config=validation_table_config(),
#             )


# # ============================================================
# # PAYMENT DETAILS
# # ============================================================

# elif page == "Payment Details":

#     st.header("🔎 Payment Details")

#     try:
#         payments = cached_payments()

#     except APIClientError as exc:

#         payments = []

#         st.error(f"Unable to load payments: {exc}")

#     payment_ids = []

#     for payment in payments:

#         payment_id = normalize_payment(payment)["payment_id"]

#         if payment_id:
#             payment_ids.append(payment_id)

#     if not payment_ids:

#         st.info("No payments are currently stored.")

#     else:

#         if st.session_state.selected_payment_id in payment_ids:
#             default_index = payment_ids.index(st.session_state.selected_payment_id)
#         else:
#             default_index = 0

#         selected_id = st.selectbox(
#             "Select Payment",
#             payment_ids,
#             index=default_index,
#         )

#         st.session_state.selected_payment_id = selected_id

#         try:

#             payment = load_single_payment(selected_id)

#         except APIClientError:

#             payment = next(
#                 (
#                     p
#                     for p in payments
#                     if normalize_payment(p)["payment_id"] == selected_id
#                 ),
#                 {},
#             )

#         p = normalize_payment(payment)

#         # ----------------------------------------------------
#         # PAYMENT INFORMATION
#         # ----------------------------------------------------

#         st.subheader("Payment Information")

#         a, b = st.columns(2)

#         with a:

#             st.text_input(
#                 "Payment ID",
#                 p["payment_id"],
#                 disabled=True,
#             )

#             st.text_input(
#                 "Amount",
#                 p["amount"],
#                 disabled=True,
#             )

#             st.text_input(
#                 "Debtor Name",
#                 p["debtor_name"],
#                 disabled=True,
#             )

#             st.text_input(
#                 "Debtor Account",
#                 p["debtor_account"],
#                 disabled=True,
#             )

#         with b:

#             st.text_input(
#                 "Currency",
#                 p["currency"],
#                 disabled=True,
#             )

#             st.text_input(
#                 "Beneficiary",
#                 p["beneficiary"],
#                 disabled=True,
#             )

#             st.text_input(
#                 "Creditor Account",
#                 p["creditor_account"],
#                 disabled=True,
#             )

#             st.text_input(
#                 "Beneficiary Address",
#                 p["beneficiary_address"],
#                 disabled=True,
#             )

#         st.divider()

#         # ----------------------------------------------------
#         # VALIDATION
#         # ----------------------------------------------------

#         st.subheader("Validation / Rejection Details")

#         try:
#             validations = cached_validation()

#         except APIClientError:
#             validations = []

#         selected_validation = next(
#             (v for v in validations if v["payment_id"] == selected_id),
#             None,
#         )

#         if not selected_validation:

#             st.info("No validation result was found " "for this payment.")

#         elif selected_validation["status"] == "VALID":

#             st.success("✅ Payment passed validation.")

#         else:

#             st.error("❌ Payment failed validation.")

#             if selected_validation["errors"]:

#                 st.write("**Validation Errors**")

#                 st.warning(selected_validation["errors"])

#             if selected_validation["warnings"]:

#                 st.write("**Validation Warnings**")

#                 st.info(selected_validation["warnings"])

#         st.divider()

#         # ----------------------------------------------------
#         # ORIGINAL / CURRENT DATA
#         # ----------------------------------------------------

#         st.subheader("Original vs Current Data")

#         original = load_optional(f"/payments/{selected_id}/original")

#         current = load_optional(f"/payments/{selected_id}/current")

#         if original is None:

#             original = (
#                 payment.get("original_data")
#                 if isinstance(
#                     payment,
#                     dict,
#                 )
#                 else None
#             )

#         if current is None:

#             current = (
#                 payment.get("current_data")
#                 if isinstance(
#                     payment,
#                     dict,
#                 )
#                 else None
#             )

#         if isinstance(original, dict) or isinstance(current, dict):

#             left, right = st.columns(2)

#             with left:
#                 st.write("**Original Data**")
#                 st.json(original or {})

#             with right:
#                 st.write("**Current Data**")
#                 st.json(current or {})

#         else:

#             st.info(
#                 "Original/current snapshots are not exposed " "by the current backend."
#             )

#         st.divider()

#         # ----------------------------------------------------
#         # CORRECTION HISTORY
#         # ----------------------------------------------------

#         st.subheader("Correction History")

#         correction_response = load_optional(f"/payments/{selected_id}/corrections")

#         correction_rows = (
#             extract_list(
#                 correction_response,
#                 [
#                     "corrections",
#                     "history",
#                     "data",
#                     "results",
#                 ],
#             )
#             if correction_response is not None
#             else []
#         )

#         if correction_rows:

#             st.dataframe(
#                 pd.DataFrame(correction_rows).fillna("").astype(str),
#                 use_container_width=True,
#                 hide_index=True,
#             )

#         else:

#             st.info("No correction history is available " "for this payment.")

#         st.divider()

#         # ----------------------------------------------------
#         # DATA LINEAGE
#         # ----------------------------------------------------

#         st.subheader("Data Lineage")

#         lineage_response = load_optional(f"/payments/{selected_id}/lineage")

#         lineage_rows = (
#             extract_list(
#                 lineage_response,
#                 [
#                     "lineage",
#                     "data",
#                     "results",
#                 ],
#             )
#             if lineage_response is not None
#             else []
#         )

#         if lineage_rows:

#             st.dataframe(
#                 pd.DataFrame(lineage_rows).fillna("").astype(str),
#                 use_container_width=True,
#                 hide_index=True,
#             )

#         else:

#             st.info("No field-level lineage is exposed " "by the current backend.")

#         st.divider()

#         # ----------------------------------------------------
#         # PAYMENT AUDIT HISTORY
#         # ----------------------------------------------------

#         st.subheader("Payment Audit History")

#         try:
#             audit_logs = cached_audit()

#         except APIClientError:
#             audit_logs = []

#         payment_logs = [x for x in audit_logs if x["payment_id"] == selected_id]

#         if payment_logs:

#             for log in payment_logs:

#                 with st.container(border=True):

#                     st.write(
#                         f"**{log['event_type']}** — "
#                         f"{log['event_status']} — "
#                         f"{log['created_at'] or 'time unavailable'}"
#                     )

#                     if log["description"]:

#                         st.write(log["description"])

#                     if log["details"]:

#                         try:
#                             st.json(json.loads(log["details"]))

#                         except Exception:
#                             st.code(log["details"])

#         else:

#             st.info("No audit history found " "for this payment.")


# # ============================================================
# # VALIDATION
# # ============================================================

# elif page == "Validation":

#     st.header("✅ Payment Validation")

#     st.write(
#         "Review deterministic validation results returned by FastAPI. "
#         "The table shows compact issue codes; select a payment below "
#         "to view the complete validation messages."
#     )

#     try:
#         validation_results = cached_validation()
#     except APIClientError as exc:
#         validation_results = []
#         st.error(f"Unable to retrieve validation results: {exc}")

#     if not validation_results:
#         st.info("No validation results are currently stored.")

#     else:
#         table = []

#         for result in validation_results:
#             table.append(
#                 {
#                     "Payment ID": result["payment_id"] or "—",
#                     "Status": result["status"] or "UNKNOWN",
#                     "Errors": issue_codes(result["errors"]),
#                     "Warnings": issue_codes(result["warnings"]),
#                     "Created At": result["created_at"] or "—",
#                 }
#             )

#         validation_df = pd.DataFrame(table)

#         st.dataframe(
#             validation_df,
#             use_container_width=True,
#             hide_index=True,
#             height=min(620, 80 + len(validation_df) * 52),
#             row_height=52,
#             column_config=validation_table_config(),
#         )

#         st.caption(
#             "Tip: the Errors and Warnings columns show codes only so the table "
#             "stays readable. Full field/message details are shown below."
#         )

#         st.divider()

#         payment_options = [
#             x["payment_id"] for x in validation_results if x.get("payment_id")
#         ]

#         if payment_options:
#             selected_id = st.selectbox(
#                 "Select Payment",
#                 payment_options,
#             )

#             selected = next(
#                 x for x in validation_results if x["payment_id"] == selected_id
#             )

#             if selected["status"] == "VALID":
#                 st.success("✅ Payment passed validation.")
#             else:
#                 st.error("❌ Payment failed validation.")

#             detail_left, detail_right = st.columns(2)

#             with detail_left:
#                 render_issue_details(
#                     "Validation Errors",
#                     selected["errors"],
#                     "error",
#                 )

#             with detail_right:
#                 render_issue_details(
#                     "Validation Warnings",
#                     selected["warnings"],
#                     "warning",
#                 )


# # ============================================================
# # AI ANALYSIS
# # ============================================================

# elif page == "AI Analysis":

#     st.header("🤖 AI Rejection Analysis")

#     st.write("Review rejection analysis generated " "by the local Ollama model.")

#     try:

#         ai_results = cached_ai()

#     except APIClientError as exc:

#         ai_results = []

#         st.error(f"Unable to retrieve AI analysis: {exc}")

#     if not ai_results:

#         st.info("No AI rejection analysis is currently stored.")

#         st.write(
#             "Process a rejected payment through " "the Phase 10 Ollama workflow first."
#         )

#     else:

#         st.success(f"{len(ai_results)} AI analysis " "result(s) found.")

#         # ----------------------------------------------------
#         # AI SUMMARY TABLE
#         # ----------------------------------------------------

#         ai_table = []

#         for result in ai_results:

#             ai_table.append(
#                 {
#                     "Payment ID": result["payment_id"],
#                     "Status": result["status"],
#                     "Severity": result["severity"],
#                     "Problematic Field": result["problematic_field"],
#                     "Rejection Reason": result["rejection_reason"],
#                 }
#             )

#         st.dataframe(
#             pd.DataFrame(ai_table).fillna("").astype(str),
#             use_container_width=True,
#             hide_index=True,
#         )

#         st.divider()

#         ai_ids = [x["payment_id"] for x in ai_results if x["payment_id"]]

#         if ai_ids:

#             selected_id = st.selectbox(
#                 "Select Payment for AI Analysis",
#                 ai_ids,
#             )

#             selected_ai = next(x for x in ai_results if x["payment_id"] == selected_id)

#             st.subheader("AI Rejection Analysis")

#             c1, c2, c3 = st.columns(3)

#             c1.metric(
#                 "Status",
#                 selected_ai["status"],
#             )

#             c2.metric(
#                 "Severity",
#                 selected_ai["severity"],
#             )

#             c3.metric(
#                 "Payment ID",
#                 selected_id,
#             )

#             if selected_ai["confidence"]:

#                 st.caption(
#                     "AI confidence/review indicator: " + selected_ai["confidence"]
#                 )

#             st.write("**Rejection Reason**")

#             st.warning(selected_ai["rejection_reason"] or "Not available")

#             st.write("**Root Cause**")

#             st.info(selected_ai["root_cause"] or "Not available")

#             st.write("**Problematic Field**")

#             st.info(selected_ai["problematic_field"] or "Not available")

#             st.write("**Recommendation / Suggested Correction**")

#             st.success(selected_ai["recommendation"] or "Not available")

#             st.write("**Explanation**")

#             st.write(selected_ai["explanation"] or "Not available")

#             # ------------------------------------------------
#             # RAG ANALYSIS
#             # ------------------------------------------------
#             # Pass the complete deterministic validation result directly
#             # to RAG. RAG must not reconstruct or hardcode an error.
#             try:
#                 validation_results_for_rag = cached_validation()

#                 selected_validation_for_rag = next(
#                     (
#                         x
#                         for x in validation_results_for_rag
#                         if x.get("payment_id") == selected_id
#                     ),
#                     None,
#                 )

#                 if selected_validation_for_rag:
#                     st.divider()
#                     show_rag_analysis(selected_validation_for_rag)
#                 else:
#                     st.info(
#                         "No deterministic validation result is available "
#                         "for RAG analysis."
#                     )

#             except Exception as exc:
#                 st.warning(f"RAG analysis unavailable: {exc}")

#             st.divider()

#             # ------------------------------------------------
#             # HUMAN REVIEW
#             # ------------------------------------------------

#             st.subheader("Human Review")

#             b1, b2 = st.columns(2)

#             with b1:

#                 if st.button(
#                     "✅ Approve Correction",
#                     use_container_width=True,
#                     type="primary",
#                 ):

#                     try:

#                         response = api_post_first(
#                             [
#                                 (f"/payments/" f"{selected_id}/" "approve-correction"),
#                                 (f"/payments/" f"{selected_id}/approve"),
#                             ],
#                             payload={"payment_id": selected_id},
#                         )

#                         cached_payments.clear()
#                         cached_validation.clear()
#                         cached_ai.clear()
#                         cached_audit.clear()

#                         st.success("Correction approved.")

#                         st.json(response)

#                     except APIClientError as exc:

#                         if "404" in str(exc):

#                             st.warning(
#                                 "The backend does not expose "
#                                 "the correction approval endpoint yet."
#                             )

#                         else:

#                             st.error(f"Approval failed: {exc}")

#             with b2:

#                 if st.button(
#                     "❌ Reject Suggestion",
#                     use_container_width=True,
#                 ):

#                     try:

#                         response = api_post_first(
#                             [
#                                 (f"/payments/" f"{selected_id}/" "reject-correction"),
#                                 (f"/payments/" f"{selected_id}/reject"),
#                             ],
#                             payload={"payment_id": selected_id},
#                         )

#                         cached_ai.clear()
#                         cached_audit.clear()

#                         st.success("AI correction suggestion rejected.")

#                         st.json(response)

#                     except APIClientError as exc:

#                         if "404" in str(exc):

#                             st.warning(
#                                 "The backend does not expose "
#                                 "the correction rejection endpoint yet."
#                             )

#                         else:

#                             st.error(f"Rejection failed: {exc}")


# # ============================================================
# # ANALYTICS
# # ============================================================

# elif page == "Analytics":

#     st.header("📊 Analytics")

#     st.write("Operational and data-quality analytics " "derived from backend records.")

#     payments, validations, ai_results = get_common_data()

#     # --------------------------------------------------------
#     # BACKEND ANALYTICS
#     # --------------------------------------------------------

#     try:

#         analytics = load_optional("/analytics/summary")

#     except APIClientError as exc:

#         analytics = None

#         st.warning(
#             "Analytics endpoint unavailable. " "Using frontend aggregation instead."
#         )

#     if isinstance(
#         analytics,
#         dict,
#     ):

#         st.subheader("Backend Analytics Summary")

#         metrics = {}

#         for key, value in analytics.items():

#             if isinstance(
#                 value,
#                 (str, int, float),
#             ):

#                 metrics[
#                     key.replace(
#                         "_",
#                         " ",
#                     ).title()
#                 ] = value

#         if metrics:

#             cols = st.columns(
#                 min(
#                     4,
#                     len(metrics),
#                 )
#             )

#             for index, (
#                 key,
#                 value,
#             ) in enumerate(metrics.items()):

#                 cols[index % len(cols)].metric(
#                     key,
#                     value,
#                 )

#     st.divider()

#     # --------------------------------------------------------
#     # REJECTION BY REASON
#     # --------------------------------------------------------

#     reason_counts = {}

#     for result in validations:

#         if result["status"] == "REJECTED":

#             reason = result["errors"] or "Unknown rejection reason"

#             reason_counts[reason] = (
#                 reason_counts.get(
#                     reason,
#                     0,
#                 )
#                 + 1
#             )

#     st.subheader("Rejection Count by Reason")

#     if reason_counts:

#         df = pd.DataFrame(
#             list(reason_counts.items()),
#             columns=[
#                 "Reason",
#                 "Count",
#             ],
#         ).set_index("Reason")

#         st.bar_chart(df)

#     else:

#         st.info("No rejected payments available " "for this chart.")

#     # --------------------------------------------------------
#     # CURRENCY DISTRIBUTION
#     # --------------------------------------------------------

#     currency_counts = {}

#     for payment in payments:

#         p = normalize_payment(payment)

#         currency = p["currency"] or "UNKNOWN"

#         currency_counts[currency] = (
#             currency_counts.get(
#                 currency,
#                 0,
#             )
#             + 1
#         )

#     st.subheader("Payment Count by Currency")

#     if currency_counts:

#         df = pd.DataFrame(
#             list(currency_counts.items()),
#             columns=[
#                 "Currency",
#                 "Payments",
#             ],
#         ).set_index("Currency")

#         st.bar_chart(df)

#     else:

#         st.info("No currency data available.")

#     # --------------------------------------------------------
#     # AI SEVERITY
#     # --------------------------------------------------------

#     severity_counts = {}

#     for result in ai_results:

#         severity = result["severity"] or "UNKNOWN"

#         severity_counts[severity] = (
#             severity_counts.get(
#                 severity,
#                 0,
#             )
#             + 1
#         )

#     st.subheader("AI Rejection Severity")

#     if severity_counts:

#         df = pd.DataFrame(
#             list(severity_counts.items()),
#             columns=[
#                 "Severity",
#                 "Payments",
#             ],
#         ).set_index("Severity")

#         st.bar_chart(df)

#     else:

#         st.info("No AI severity data available.")


# # ============================================================
# # AUDIT TRAIL
# # ============================================================

# elif page == "Audit Trail":

#     st.header("📜 Audit Trail")

#     st.write(
#         "Track payment processing events, validation, "
#         "AI analysis, corrections, and data-lineage events."
#     )

#     if st.button("🔄 Refresh Audit Trail"):

#         cached_audit.clear()

#         refresh_all()

#     try:

#         audit_logs = cached_audit()

#     except APIClientError as exc:

#         audit_logs = []

#         st.error(f"❌ Unable to retrieve audit logs: {exc}")

#     total_events = len(audit_logs)

#     successful_events = sum(
#         x["event_status"]
#         in {
#             "SUCCESS",
#             "COMPLETED",
#             "VALID",
#         }
#         for x in audit_logs
#     )

#     failed_events = sum(
#         x["event_status"]
#         in {
#             "FAILED",
#             "ERROR",
#             "REJECTED",
#         }
#         for x in audit_logs
#     )

#     c1, c2, c3 = st.columns(3)

#     c1.metric(
#         "Total Audit Events",
#         total_events,
#     )

#     c2.metric(
#         "Successful Events",
#         successful_events,
#     )

#     c3.metric(
#         "Failed Events",
#         failed_events,
#     )

#     st.divider()

#     if not audit_logs:

#         st.info(
#             "No audit events found yet. " "Upload and process a payment file first."
#         )

#     else:

#         st.subheader("Processing History")

#         event_types = sorted({x["event_type"] or "UNKNOWN" for x in audit_logs})

#         selected_event = st.selectbox(
#             "Filter by Event Type",
#             ["All"] + event_types,
#         )

#         filtered = [
#             x
#             for x in audit_logs
#             if (selected_event == "All" or x["event_type"] == selected_event)
#         ]

#         st.write(
#             f"Showing **{len(filtered)}** " f"of **{len(audit_logs)}** audit events"
#         )

#         audit_table = [
#             {
#                 "Event": x["event_type"],
#                 "Status": x["event_status"],
#                 "Payment ID": x["payment_id"],
#                 "Description": x["description"],
#                 "Created At": x["created_at"],
#             }
#             for x in filtered
#         ]

#         st.dataframe(
#             pd.DataFrame(audit_table).fillna("").astype(str),
#             use_container_width=True,
#             hide_index=True,
#         )

#         st.divider()

#         st.subheader("Detailed Audit Events")

#         for log in filtered:

#             label = (
#                 f"{log['event_type']} — "
#                 f"{log['event_status']} — "
#                 f"{log['payment_id'] or 'File-level event'}"
#             )

#             with st.expander(label):

#                 a, b = st.columns(2)

#                 with a:

#                     st.write("**Event Type**")

#                     st.write(log["event_type"])

#                     st.write("**Event Status**")

#                     st.write(log["event_status"])

#                 with b:

#                     st.write("**Payment ID**")

#                     st.write(log["payment_id"] or "-")

#                     st.write("**Created At**")

#                     st.write(log["created_at"] or "-")

#                 if log["description"]:

#                     st.write("**Description**")

#                     st.write(log["description"])

#                 if log["details"]:

#                     st.write("**Details**")

#                     try:

#                         st.json(json.loads(log["details"]))

#                     except Exception:

#                         st.code(log["details"])


# # ============================================================
# # FOOTER
# # ============================================================

# st.divider()

# st.caption("PayFlow Intelligence • Streamlit frontend • " f"FastAPI: {API_BASE_URL}")


"""
Payment Processing Backend
==========================

FastAPI backend for the PayFlow payment-processing project.

Features:
- ISO 20022 XML upload
- XML parsing
- Payment extraction
- Validation
- Local Ollama AI analysis
- SQLite persistence
- Audit logs
- Payment lookup
- Validation results
- AI rejection results
- Analytics
- Health checks

No OpenAI API required.
"""

import csv
import io
import json
import math
import sqlite3
import uuid
import xml.etree.ElementTree as ET

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# ============================================================
# PROJECT CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = DATA_DIR / "payflow.db"


# ============================================================
# APP CONFIGURATION
# ============================================================

app = FastAPI(
    title="Payment Processing API",
    description="ISO 20022 Payment Processing and AI Rejection Analysis API",
    version="2.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DATABASE
# ============================================================


def get_db():
    connection = sqlite3.connect(str(DATABASE_PATH))
    connection.row_factory = sqlite3.Row
    return connection


def init_database():
    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            payment_id TEXT PRIMARY KEY,
            message_id TEXT,
            instruction_id TEXT,
            end_to_end_id TEXT,
            transaction_id TEXT,
            amount TEXT,
            currency TEXT,
            debtor_name TEXT,
            creditor_name TEXT,
            debtor_account TEXT,
            creditor_account TEXT,
            debtor_address TEXT,
            creditor_address TEXT,
            remittance_information TEXT,
            creation_datetime TEXT,
            file_name TEXT,
            uploaded_at TEXT,
            updated_at TEXT
        )
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS validation_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payment_id TEXT NOT NULL,
            status TEXT,
            valid INTEGER,
            error_count INTEGER,
            warning_count INTEGER,
            errors TEXT,
            warnings TEXT,
            validated_at TEXT
        )
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_rejections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payment_id TEXT NOT NULL,
            result TEXT,
            created_at TEXT
        )
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id TEXT PRIMARY KEY,
            timestamp TEXT,
            action TEXT,
            status TEXT,
            payment_id TEXT,
            details TEXT
        )
        """)

    connection.commit()
    connection.close()


init_database()


# ============================================================
# DATABASE HELPERS
# ============================================================


def payment_row_to_dict(row):
    if row is None:
        return None

    return dict(row)


def get_payment_from_db(payment_id: str):
    connection = get_db()

    row = connection.execute(
        """
        SELECT *
        FROM payments
        WHERE payment_id = ?
        """,
        (payment_id,),
    ).fetchone()

    connection.close()

    return payment_row_to_dict(row)


def get_all_payments_from_db():
    connection = get_db()

    rows = connection.execute("""
        SELECT *
        FROM payments
        ORDER BY updated_at DESC
        """).fetchall()

    connection.close()

    return [dict(row) for row in rows]


def save_payment_to_db(payment: Dict[str, Any]):
    now = datetime.utcnow().isoformat()

    connection = get_db()

    connection.execute(
        """
        INSERT INTO payments (
            payment_id,
            message_id,
            instruction_id,
            end_to_end_id,
            transaction_id,
            amount,
            currency,
            debtor_name,
            creditor_name,
            debtor_account,
            creditor_account,
            debtor_address,
            creditor_address,
            remittance_information,
            creation_datetime,
            file_name,
            uploaded_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(payment_id)
        DO UPDATE SET
            message_id = excluded.message_id,
            instruction_id = excluded.instruction_id,
            end_to_end_id = excluded.end_to_end_id,
            transaction_id = excluded.transaction_id,
            amount = excluded.amount,
            currency = excluded.currency,
            debtor_name = excluded.debtor_name,
            creditor_name = excluded.creditor_name,
            debtor_account = excluded.debtor_account,
            creditor_account = excluded.creditor_account,
            debtor_address = excluded.debtor_address,
            creditor_address = excluded.creditor_address,
            remittance_information = excluded.remittance_information,
            creation_datetime = excluded.creation_datetime,
            file_name = excluded.file_name,
            uploaded_at = excluded.uploaded_at,
            updated_at = excluded.updated_at
        """,
        (
            payment.get("payment_id"),
            payment.get("message_id", ""),
            payment.get("instruction_id", ""),
            payment.get("end_to_end_id", ""),
            payment.get("transaction_id", ""),
            payment.get("amount", ""),
            payment.get("currency", ""),
            payment.get("debtor_name", ""),
            payment.get("creditor_name", ""),
            payment.get("debtor_account", ""),
            payment.get("creditor_account", ""),
            payment.get("debtor_address", ""),
            payment.get("creditor_address", ""),
            payment.get("remittance_information", ""),
            payment.get("creation_datetime", ""),
            payment.get("file_name", ""),
            payment.get("uploaded_at", now),
            now,
        ),
    )

    connection.commit()
    connection.close()


def save_validation_to_db(validation: Dict[str, Any]):
    connection = get_db()

    connection.execute(
        """
        INSERT INTO validation_results (
            payment_id,
            status,
            valid,
            error_count,
            warning_count,
            errors,
            warnings,
            validated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            validation.get("payment_id"),
            validation.get("status"),
            1 if validation.get("valid") else 0,
            validation.get("error_count", 0),
            validation.get("warning_count", 0),
            json.dumps(validation.get("errors", [])),
            json.dumps(validation.get("warnings", [])),
            validation.get("validated_at"),
        ),
    )

    connection.commit()
    connection.close()


def save_ai_result_to_db(result: Dict[str, Any]):
    connection = get_db()

    connection.execute(
        """
        INSERT INTO ai_rejections (
            payment_id,
            result,
            created_at
        )
        VALUES (?, ?, ?)
        """,
        (
            result.get("payment_id"),
            json.dumps(result),
            datetime.utcnow().isoformat(),
        ),
    )

    connection.commit()
    connection.close()


def create_audit_log(
    action: str,
    status: str,
    payment_id: Optional[str] = None,
    details: Optional[str] = None,
):
    connection = get_db()

    connection.execute(
        """
        INSERT INTO audit_logs (
            id,
            timestamp,
            action,
            status,
            payment_id,
            details
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            str(uuid.uuid4()),
            datetime.utcnow().isoformat(),
            action,
            status,
            payment_id,
            details or "",
        ),
    )

    connection.commit()
    connection.close()


# ============================================================
# XML HELPERS
# ============================================================


def get_local_name(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]

    return tag


def clean_text(value: Optional[str]) -> str:
    if value is None:
        return ""

    return value.strip()


def find_first_text(
    root: Optional[ET.Element],
    names: List[str],
) -> str:

    if root is None:
        return ""

    wanted = set(names)

    for element in root.iter():

        local_name = get_local_name(element.tag)

        if local_name in wanted:

            text = clean_text(element.text)

            if text:
                return text

    return ""


# ============================================================
# PAYMENT PARSER
# ============================================================


def parse_payment_scope(
    scope: ET.Element,
    document: ET.Element,
) -> Dict[str, Any]:
    """
    Extract one payment transaction.

    ISO 20022 commonly places the debtor under PmtInf rather than
    inside every CdtTrfTxInf transaction. When it is not present
    inside the transaction, inherit the debtor from the same PmtInf.
    """

    def text(names: List[str]) -> str:
        return find_first_text(scope, names)

    # ------------------------------------------------------------
    # AMOUNT + CURRENCY
    # ------------------------------------------------------------
    amount = ""
    currency = ""

    for element in scope.iter():
        if get_local_name(element.tag) == "InstdAmt":
            amount = clean_text(element.text)
            currency = element.attrib.get("Ccy", "")
            break

    # Support simple test XML.
    if not amount:
        amount = text(["amount", "Amount"])

    if not currency:
        currency = text(["currency", "Currency"])

    # ------------------------------------------------------------
    # DEBTOR
    # ------------------------------------------------------------
    # First: debtor directly inside this transaction.
    debtor = next(
        (element for element in scope.iter() if get_local_name(element.tag) == "Dbtr"),
        None,
    )

    # Second: debtor belonging to the same PmtInf block.
    if debtor is None:
        for parent in document.iter():
            if get_local_name(parent.tag) != "PmtInf":
                continue

            if any(child is scope for child in parent.iter()):
                debtor = next(
                    (
                        element
                        for element in parent.iter()
                        if get_local_name(element.tag) == "Dbtr"
                    ),
                    None,
                )
                break

    # Third: document-level fallback for simple/custom XML.
    if debtor is None:
        debtor = next(
            (
                element
                for element in document.iter()
                if get_local_name(element.tag) == "Dbtr"
            ),
            None,
        )

    # ------------------------------------------------------------
    # CREDITOR
    # ------------------------------------------------------------
    creditor = next(
        (
            element
            for element in scope.iter()
            if get_local_name(element.tag) in {"Cdtr", "Creditor"}
        ),
        None,
    )

    def scoped_text(
        element: Optional[ET.Element],
        names: List[str],
    ) -> str:
        return find_first_text(element, names)

    # ------------------------------------------------------------
    # IDENTIFIERS
    # ------------------------------------------------------------
    payment_id = (
        text(["InstrId", "InstructionIdentification"])
        or text(["EndToEndId", "EndToEndIdentification"])
        or text(["TxId", "TransactionIdentification"])
        or text(["payment_id", "PaymentId"])
    )

    # ------------------------------------------------------------
    # NAMES
    # ------------------------------------------------------------
    debtor_name = scoped_text(
        debtor,
        ["Nm", "DebtorName", "debtor_name"],
    )

    creditor_name = scoped_text(
        creditor,
        ["Nm", "CreditorName", "beneficiary", "Beneficiary"],
    )

    # Support simple XML without Dbtr/Cdtr containers.
    if not debtor_name:
        debtor_name = text(["debtor_name", "DebtorName"])

    if not creditor_name:
        creditor_name = text(
            ["creditor_name", "CreditorName", "beneficiary", "Beneficiary"]
        )

    # ------------------------------------------------------------
    # ACCOUNTS
    # ------------------------------------------------------------
    debtor_account = scoped_text(
        debtor,
        ["IBAN", "Othr", "debtor_account"],
    )

    creditor_account = scoped_text(
        creditor,
        ["IBAN", "Othr", "creditor_account"],
    )

    if not debtor_account:
        debtor_account = text(["debtor_account"])

    if not creditor_account:
        creditor_account = text(["creditor_account"])

    # ------------------------------------------------------------
    # ADDRESSES
    # ------------------------------------------------------------
    debtor_address = scoped_text(
        debtor,
        ["AdrLine", "PstlAdr", "debtor_address"],
    )

    creditor_address = scoped_text(
        creditor,
        ["AdrLine", "PstlAdr", "beneficiary_address", "creditor_address"],
    )

    if not debtor_address:
        debtor_address = text(["debtor_address"])

    if not creditor_address:
        creditor_address = text(["beneficiary_address", "creditor_address"])

    return {
        "message_id": find_first_text(
            document,
            ["MsgId", "MessageIdentification", "message_id"],
        ),
        "payment_id": payment_id,
        "instruction_id": text(
            ["InstrId", "InstructionIdentification", "instruction_id"]
        ),
        "end_to_end_id": text(
            ["EndToEndId", "EndToEndIdentification", "end_to_end_id"]
        ),
        "transaction_id": text(["TxId", "TransactionIdentification", "transaction_id"]),
        "amount": amount,
        "currency": currency,
        "debtor_name": debtor_name,
        "creditor_name": creditor_name,
        "debtor_account": debtor_account,
        "creditor_account": creditor_account,
        "debtor_address": debtor_address,
        "creditor_address": creditor_address,
        "remittance_information": text(["Ustrd", "remittance_information"]),
        "creation_datetime": find_first_text(
            document,
            ["CreDtTm", "CreationDateTime", "creation_datetime"],
        ),
    }


def parse_payments_xml(
    xml_content: bytes,
) -> List[Dict[str, Any]]:

    try:

        root = ET.fromstring(xml_content)

    except ET.ParseError as error:

        raise HTTPException(
            status_code=400,
            detail=f"Invalid XML file: {error}",
        )

    transactions = [
        element
        for element in root.iter()
        if get_local_name(element.tag)
        in {
            "CdtTrfTxInf",
            "CreditTransferTransactionInformation",
            "Payment",
            "payment",
        }
    ]

    scopes = transactions or [root]

    return [parse_payment_scope(scope, root) for scope in scopes]


def parse_payment_xml(
    xml_content: bytes,
) -> Dict[str, Any]:

    parsed_payments = parse_payments_xml(xml_content)

    if not parsed_payments:

        raise HTTPException(
            status_code=400,
            detail="No payment found.",
        )

    return parsed_payments[0]


# ============================================================
# VALIDATION ENGINE
# ============================================================


def validate_payment(
    payment: Dict[str, Any],
) -> Dict[str, Any]:

    errors = []
    warnings = []

    # --------------------------------------------------------
    # TRANSACTION ID
    # --------------------------------------------------------

    transaction_identifier = (
        payment.get("payment_id")
        or payment.get("instruction_id")
        or payment.get("end_to_end_id")
        or payment.get("transaction_id")
    )

    if not transaction_identifier:

        errors.append(
            {
                "field": "transaction_id",
                "code": "MISSING_TRANSACTION_ID",
                "message": "Transaction identification is missing.",
            }
        )

    # --------------------------------------------------------
    # AMOUNT
    # --------------------------------------------------------

    amount = payment.get("amount")

    if not amount:

        errors.append(
            {
                "field": "amount",
                "code": "MISSING_AMOUNT",
                "message": "Payment amount is missing.",
            }
        )

    else:

        try:

            numeric_amount = float(amount)

            if not math.isfinite(numeric_amount) or numeric_amount <= 0:

                errors.append(
                    {
                        "field": "amount",
                        "code": "INVALID_AMOUNT",
                        "message": "Payment amount must be greater than zero.",
                    }
                )

        except (ValueError, TypeError):

            errors.append(
                {
                    "field": "amount",
                    "code": "INVALID_AMOUNT_FORMAT",
                    "message": "Payment amount is not numeric.",
                }
            )

    # --------------------------------------------------------
    # CURRENCY
    # --------------------------------------------------------

    if not payment.get("currency"):

        warnings.append(
            {
                "field": "currency",
                "code": "MISSING_CURRENCY",
                "message": "Currency information was not found.",
            }
        )

    # --------------------------------------------------------
    # DEBTOR
    # --------------------------------------------------------

    if not (payment.get("debtor_name") or payment.get("debtor")):

        errors.append(
            {
                "field": "debtor_name",
                "code": "MISSING_DEBTOR",
                "message": "Debtor information is missing.",
            }
        )

    # --------------------------------------------------------
    # CREDITOR
    # --------------------------------------------------------

    if not (payment.get("creditor_name") or payment.get("beneficiary")):

        errors.append(
            {
                "field": "creditor_name",
                "code": "MISSING_CREDITOR",
                "message": "Creditor information is missing.",
            }
        )

    status = "REJECTED" if errors else "ACCEPTED"

    return {
        "payment_id": (transaction_identifier or payment.get("payment_id")),
        "status": status,
        "valid": len(errors) == 0,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "validated_at": datetime.utcnow().isoformat(),
    }


# ============================================================
# OLLAMA AI ANALYSIS
# ============================================================


def analyze_with_ollama(
    payment: Dict[str, Any],
    validation: Dict[str, Any],
) -> Dict[str, Any]:

    try:

        from backend.services.ai_rejection_analyzer import (
            analyze_rejection,
        )

        result = analyze_rejection(
            payment,
            validation,
        )

        result["payment_id"] = payment.get("payment_id")

        return result

    except Exception:
        pass

    try:

        import ollama

    except ImportError:

        return {
            "status": "ERROR",
            "rejection_reason": "Ollama Python package is not installed.",
            "root_cause": "Missing ollama package.",
            "severity": "MEDIUM",
            "problematic_field": "System",
            "recommendation": "Install the ollama Python package.",
            "explanation": "AI analysis could not be executed.",
            "payment_id": payment.get("payment_id"),
        }

    prompt = f"""
You are a financial payment analysis assistant.

Analyze this ISO 20022 payment.

PAYMENT:

{json.dumps(payment, indent=2, default=str)}

VALIDATION RESULT:

{json.dumps(validation, indent=2, default=str)}

Determine:

1. Whether the payment is rejected.
2. Main rejection reason.
3. Root cause.
4. Severity.
5. Problematic field.
6. Recommended fix.
7. Human-readable explanation.

Return ONLY valid JSON:

{{
    "status": "REJECTED or ACCEPTED",
    "rejection_reason": "string",
    "root_cause": "string",
    "severity": "LOW, MEDIUM, HIGH or CRITICAL",
    "problematic_field": "string",
    "recommendation": "string",
    "explanation": "string"
}}
"""

    try:

        response = ollama.chat(
            model="llama3.2",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You analyze ISO 20022 payment validation "
                        "failures. Do not invent information."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        response_text = response["message"]["content"].strip()

        if response_text.startswith("```json"):
            response_text = response_text[7:]

        elif response_text.startswith("```"):
            response_text = response_text[3:]

        if response_text.endswith("```"):
            response_text = response_text[:-3]

        response_text = response_text.strip()

        try:

            result = json.loads(response_text)

        except json.JSONDecodeError:

            result = {
                "status": "REJECTED",
                "rejection_reason": ("AI returned an unstructured response"),
                "root_cause": ("Unable to parse AI response"),
                "severity": "MEDIUM",
                "problematic_field": "Unknown",
                "recommendation": ("Review validation errors manually."),
                "explanation": response_text,
            }

        result["payment_id"] = payment.get("payment_id")

        return result

    except Exception as error:

        return {
            "status": "ERROR",
            "rejection_reason": "AI analysis failed",
            "root_cause": str(error),
            "severity": "MEDIUM",
            "problematic_field": "AI service",
            "recommendation": (
                "Check that Ollama is running " "and llama3.2 is installed."
            ),
            "explanation": (
                "The payment was processed, " "but AI analysis could not be completed."
            ),
            "payment_id": payment.get("payment_id"),
        }


# ============================================================
# HEALTH
# ============================================================


@app.get("/")
def root():

    return {
        "status": "success",
        "message": "Payment Processing API is running.",
        "docs": "/docs",
        "database": str(DATABASE_PATH),
    }


@app.get("/health")
def health_check():

    return {
        "status": "success",
        "service": "payment-processing-backend",
        "database": "connected",
        "timestamp": datetime.utcnow().isoformat(),
    }


# ============================================================
# OLLAMA HEALTH
# ============================================================


@app.get("/ai/health")
def ai_health():

    try:

        import ollama

        models = ollama.list()

        installed_models = []

        for model in models.get("models", []):

            name = model.get("name")

            if name:
                installed_models.append(name)

        model_available = any(
            name == "llama3.2" or name.startswith("llama3.2:")
            for name in installed_models
        )

        return {
            "status": "success",
            "ollama_running": True,
            "model": "llama3.2",
            "model_available": model_available,
            "installed_models": installed_models,
        }

    except Exception as error:

        return {
            "status": "error",
            "ollama_running": False,
            "model": "llama3.2",
            "model_available": False,
            "installed_models": [],
            "error": str(error),
        }


# ============================================================
# UPLOAD PAYMENT FILE
# ============================================================


@app.post("/upload/")
async def upload_payment_file(
    file: UploadFile = File(...),
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file selected.",
        )

    allowed_extensions = {
        ".xml",
        ".json",
        ".csv",
    }

    filename_lower = file.filename.lower()

    if not any(filename_lower.endswith(extension) for extension in allowed_extensions):

        raise HTTPException(
            status_code=400,
            detail=("Unsupported file type. " "Use XML, JSON or CSV."),
        )

    content = await file.read()

    if not content:

        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    # --------------------------------------------------------
    # PARSE
    # --------------------------------------------------------

    try:

        if filename_lower.endswith(".xml"):

            parsed_payments = parse_payments_xml(content)

        elif filename_lower.endswith(".json"):

            parsed_data = json.loads(content.decode("utf-8"))

            parsed_payments = (
                parsed_data
                if isinstance(parsed_data, list)
                else parsed_data.get(
                    "payments",
                    [parsed_data],
                )
            )

        else:

            parsed_payments = list(csv.DictReader(io.StringIO(content.decode("utf-8"))))

    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        TypeError,
        AttributeError,
        csv.Error,
    ) as error:

        raise HTTPException(
            status_code=400,
            detail=f"Unable to parse file: {error}",
        )

    if not parsed_payments:

        raise HTTPException(
            status_code=400,
            detail=("No payment records found " "in the uploaded file."),
        )

    # --------------------------------------------------------
    # PROCESS
    # --------------------------------------------------------

    processed_payments = []
    processed_validations = []
    processed_ai_results = []

    created_count = 0
    updated_count = 0

    for raw_payment in parsed_payments:

        if not isinstance(raw_payment, dict):

            raise HTTPException(
                status_code=400,
                detail=("Each payment record " "must be an object."),
            )

        payment = dict(raw_payment)

        # Preserve the original identifier state for validation.
        # Do not generate an ID before validation.
        payment["instruction_id"] = payment.get("instruction_id") or payment.get(
            "payment_id"
        )

        payment["creditor_name"] = payment.get("creditor_name") or payment.get(
            "beneficiary"
        )

        payment["file_name"] = file.filename
        payment["uploaded_at"] = datetime.utcnow().isoformat()

        # Validate before assigning an internal storage ID.
        validation = validate_payment(payment)

        # SQLite requires a primary key. If the incoming payment has no
        # identifier, generate an internal ID AFTER validation so the
        # missing-ID validation error is preserved.
        payment_id = (
            payment.get("payment_id")
            or payment.get("instruction_id")
            or payment.get("end_to_end_id")
            or payment.get("transaction_id")
        )

        if not payment_id:
            payment_id = f"PAY-{uuid.uuid4().hex[:8].upper()}"
            payment["payment_id"] = payment_id
        else:
            payment["payment_id"] = payment_id

        # Validation intentionally runs before an internal ID is generated so
        # missing identifiers are still reported. Attach the final storage ID
        # before persisting the validation result.
        validation["payment_id"] = payment_id
        validation["valid"] = validation.get("status") in {"VALID", "ACCEPTED"}
        validation["error_count"] = len(validation.get("field_errors", []))
        validation["warning_count"] = len(validation.get("warnings", []))
        validation["validated_at"] = datetime.utcnow().isoformat()

        # ----------------------------------------------------
        # CHECK EXISTING PAYMENT
        # ----------------------------------------------------

        existing_payment = get_payment_from_db(payment_id)

        if existing_payment:

            updated_count += 1

            create_audit_log(
                action="PAYMENT_UPDATED",
                status="UPDATED",
                payment_id=payment_id,
                details=(f"Payment reprocessed from " f"file '{file.filename}'."),
            )

        else:

            created_count += 1

            create_audit_log(
                action="PAYMENT_CREATED",
                status="CREATED",
                payment_id=payment_id,
                details=(f"New payment received from " f"file '{file.filename}'."),
            )

        # ----------------------------------------------------
        # DATABASE
        # ----------------------------------------------------

        save_payment_to_db(payment)

        save_validation_to_db(validation)

        # ----------------------------------------------------
        # AI
        # ----------------------------------------------------

        ai_result = None

        if validation["status"] in {"REJECTED", "INVALID"}:

            ai_result = analyze_with_ollama(
                payment,
                validation,
            )

            save_ai_result_to_db(ai_result)

            processed_ai_results.append(ai_result)

        # ----------------------------------------------------
        # AUDIT
        # ----------------------------------------------------

        create_audit_log(
            action="PAYMENT_PROCESSED",
            status=validation["status"],
            payment_id=payment_id,
            details=(f"File '{file.filename}' " f"uploaded, parsed and validated."),
        )

        processed_payments.append(payment)

        processed_validations.append(validation)

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {
        "status": "success",
        "message": (
            f"{len(processed_payments)} " f"payment(s) processed successfully."
        ),
        "file_name": file.filename,
        "count": len(processed_payments),
        "total_payments": len(processed_payments),
        "valid_payments": sum(
            1
            for item in processed_validations
            if item["status"] in {"ACCEPTED", "VALID"}
        ),
        "invalid_payments": sum(
            1
            for item in processed_validations
            if item["status"] in {"REJECTED", "INVALID"}
        ),
        "created_payments": created_count,
        "updated_payments": updated_count,
        "payments": processed_payments,
        "validations": processed_validations,
        "validation_results": processed_validations,
        "ai_analyses": processed_ai_results,
        "ai_rejections": processed_ai_results,
        "payment": processed_payments[0],
        "validation": processed_validations[0],
        "ai_analysis": (processed_ai_results[0] if processed_ai_results else None),
    }


# ============================================================
# GET ALL PAYMENTS
# ============================================================


@app.get("/payments/")
def get_payments():

    all_payments = get_all_payments_from_db()

    return {
        "status": "success",
        "count": len(all_payments),
        "payments": all_payments,
    }


# ============================================================
# GET SINGLE PAYMENT
# ============================================================


@app.get("/payments/{payment_id}")
def get_payment(payment_id: str):

    payment = get_payment_from_db(payment_id)

    if payment is None:

        raise HTTPException(
            status_code=404,
            detail=(f"Payment '{payment_id}' " f"not found."),
        )

    return {
        "status": "success",
        "payment": payment,
    }


# ============================================================
# GET VALIDATION RESULTS
# ============================================================


@app.get("/validation/")
def get_validation_results():

    connection = get_db()

    rows = connection.execute("""
        SELECT *
        FROM validation_results
        ORDER BY id DESC
        """).fetchall()

    connection.close()

    results = []

    for row in rows:

        item = dict(row)

        try:
            item["errors"] = json.loads(item.get("errors") or "[]")
        except Exception:
            item["errors"] = []

        try:
            item["warnings"] = json.loads(item.get("warnings") or "[]")
        except Exception:
            item["warnings"] = []

        item["valid"] = bool(item.get("valid"))

        results.append(item)

    return {
        "status": "success",
        "count": len(results),
        "validation_results": results,
    }


# ============================================================
# GET AI REJECTIONS
# ============================================================


@app.get("/ai/rejections")
def get_ai_rejections():

    connection = get_db()

    rows = connection.execute("""
        SELECT *
        FROM ai_rejections
        ORDER BY id DESC
        """).fetchall()

    connection.close()

    results = []

    for row in rows:

        try:

            result = json.loads(row["result"])

        except Exception:

            result = {
                "payment_id": row["payment_id"],
                "status": "ERROR",
                "explanation": row["result"],
            }

        results.append(result)

    return {
        "status": "success",
        "count": len(results),
        "rejections": results,
    }


# ============================================================
# AUDIT LOGS
# ============================================================


@app.get("/audit-logs/")
def get_audit_logs():

    connection = get_db()

    rows = connection.execute("""
        SELECT *
        FROM audit_logs
        ORDER BY timestamp DESC
        """).fetchall()

    connection.close()

    return {
        "status": "success",
        "count": len(rows),
        "audit_logs": [dict(row) for row in rows],
    }


# ============================================================
# PAYMENT AUDIT LOGS
# ============================================================


@app.get("/payments/{payment_id}/audit-logs")
def get_payment_audit_logs(
    payment_id: str,
):

    connection = get_db()

    rows = connection.execute(
        """
        SELECT *
        FROM audit_logs
        WHERE payment_id = ?
        ORDER BY timestamp DESC
        """,
        (payment_id,),
    ).fetchall()

    connection.close()

    return {
        "status": "success",
        "payment_id": payment_id,
        "count": len(rows),
        "audit_logs": [dict(row) for row in rows],
    }


# ============================================================
# PAYMENT HELPER
# ============================================================


def _find_payment_or_404(
    payment_id: str,
) -> Dict[str, Any]:

    payment = get_payment_from_db(payment_id)

    if payment is None:

        raise HTTPException(
            status_code=404,
            detail=(f"Payment '{payment_id}' " f"not found."),
        )

    return payment


# ============================================================
# ORIGINAL PAYMENT
# ============================================================


@app.get("/payments/{payment_id}/original")
def get_original_payment(
    payment_id: str,
):

    payment = _find_payment_or_404(payment_id)

    return {
        "status": "success",
        "payment_id": payment_id,
        "original_data": payment,
    }


# ============================================================
# CURRENT PAYMENT
# ============================================================


@app.get("/payments/{payment_id}/current")
def get_current_payment(
    payment_id: str,
):

    payment = _find_payment_or_404(payment_id)

    return {
        "status": "success",
        "payment_id": payment_id,
        "current_data": payment,
    }


# ============================================================
# CORRECTIONS
# ============================================================


@app.get("/payments/{payment_id}/corrections")
def get_payment_corrections(
    payment_id: str,
):

    _find_payment_or_404(payment_id)

    connection = get_db()

    rows = connection.execute(
        """
        SELECT *
        FROM audit_logs
        WHERE payment_id = ?
        AND action IN (
            'CORRECTION_APPROVED',
            'CORRECTION_REJECTED'
        )
        ORDER BY timestamp DESC
        """,
        (payment_id,),
    ).fetchall()

    connection.close()

    corrections = [dict(row) for row in rows]

    return {
        "status": "success",
        "count": len(corrections),
        "corrections": corrections,
    }


# ============================================================
# LINEAGE
# ============================================================


@app.get("/payments/{payment_id}/lineage")
def get_payment_lineage(
    payment_id: str,
):

    payment = _find_payment_or_404(payment_id)

    return {
        "status": "success",
        "lineage": [
            {
                "payment_id": payment_id,
                "source_file": payment.get(
                    "file_name",
                    "",
                ),
                "uploaded_at": payment.get(
                    "uploaded_at",
                    "",
                ),
                "updated_at": payment.get(
                    "updated_at",
                    "",
                ),
                "stage": "uploaded",
            }
        ],
    }


# ============================================================
# APPROVE CORRECTION
# ============================================================


@app.post("/payments/{payment_id}/approve-correction")
@app.post("/payments/{payment_id}/approve")
def approve_payment_correction(
    payment_id: str,
):

    _find_payment_or_404(payment_id)

    create_audit_log(
        "CORRECTION_APPROVED",
        "APPROVED",
        payment_id,
        "Correction approved by user.",
    )

    return {
        "status": "success",
        "payment_id": payment_id,
        "decision": "APPROVED",
    }


# ============================================================
# REJECT CORRECTION
# ============================================================


@app.post("/payments/{payment_id}/reject-correction")
@app.post("/payments/{payment_id}/reject")
def reject_payment_correction(
    payment_id: str,
):

    _find_payment_or_404(payment_id)

    create_audit_log(
        "CORRECTION_REJECTED",
        "REJECTED",
        payment_id,
        "Correction rejected by user.",
    )

    return {
        "status": "success",
        "payment_id": payment_id,
        "decision": "REJECTED",
    }


# ============================================================
# ANALYTICS
# ============================================================


@app.get("/analytics/summary")
def get_analytics_summary():

    connection = get_db()

    total = connection.execute("""
        SELECT COUNT(*)
        FROM payments
        """).fetchone()[0]

    accepted = connection.execute("""
        SELECT COUNT(*)
        FROM validation_results
        WHERE status = 'ACCEPTED'
        """).fetchone()[0]

    rejected = connection.execute("""
        SELECT COUNT(*)
        FROM validation_results
        WHERE status = 'REJECTED'
        """).fetchone()[0]

    ai_count = connection.execute("""
        SELECT COUNT(*)
        FROM ai_rejections
        """).fetchone()[0]

    audit_count = connection.execute("""
        SELECT COUNT(*)
        FROM audit_logs
        """).fetchone()[0]

    connection.close()

    return {
        "status": "success",
        "total_payments": total,
        "accepted_payments": accepted,
        "rejected_payments": rejected,
        "ai_rejections": ai_count,
        "audit_events": audit_count,
    }
