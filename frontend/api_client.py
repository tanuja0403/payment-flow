import requests


# ============================================================
# BACKEND URL
# ============================================================

API_BASE_URL = "http://127.0.0.1:8000"


# ============================================================
# CUSTOM API ERROR
# ============================================================

class APIClientError(Exception):
    """
    Custom error for API communication problems.
    """
    pass


# ============================================================
# RESPONSE HANDLER
# ============================================================

def _handle_response(response):
    """
    Handle FastAPI responses and convert API errors
    into user-friendly messages.
    """

    if response.ok:

        try:
            return response.json()

        except ValueError:

            raise APIClientError(
                "Backend returned an invalid JSON response."
            )


    # --------------------------------------------------------
    # TRY TO READ BACKEND ERROR
    # --------------------------------------------------------

    try:

        error_data = response.json()

        detail = error_data.get(
            "detail",
            "Unknown backend error."
        )

    except ValueError:

        detail = (
            response.text
            or "Unknown backend error."
        )


    # --------------------------------------------------------
    # HTTP 400
    # --------------------------------------------------------

    if response.status_code == 400:

        raise APIClientError(
            f"Request could not be processed: {detail}"
        )


    # --------------------------------------------------------
    # HTTP 404
    # --------------------------------------------------------

    if response.status_code == 404:

        raise APIClientError(
            f"Resource not found: {detail}"
        )


    # --------------------------------------------------------
    # HTTP 500
    # --------------------------------------------------------

    if response.status_code == 500:

        raise APIClientError(
            f"Backend error: {detail}"
        )


    # --------------------------------------------------------
    # OTHER ERRORS
    # --------------------------------------------------------

    raise APIClientError(
        f"API error ({response.status_code}): {detail}"
    )


# ============================================================
# GENERIC REQUEST FUNCTION
# ============================================================

def _make_request(
    method,
    url,
    **kwargs
):
    """
    Send an HTTP request to the FastAPI backend.

    Handles:
        - API errors
        - connection errors
        - timeout errors
        - network errors
    """

    try:

        response = requests.request(
            method,
            url,
            **kwargs
        )

        return _handle_response(
            response
        )


    except requests.exceptions.ConnectionError:

        raise APIClientError(
            "Unable to connect to the FastAPI backend. "
            "Make sure the backend is running."
        )


    except requests.exceptions.Timeout:

        raise APIClientError(
            "The request timed out. "
            "Please try again."
        )


    except requests.exceptions.RequestException as error:

        raise APIClientError(
            "Network error while communicating "
            f"with backend: {error}"
        )


# ============================================================
# HEALTH CHECK
# ============================================================

def check_backend_health():

    return _make_request(
        "GET",
        f"{API_BASE_URL}/health",
        timeout=10
    )


# ============================================================
# GET ALL PAYMENTS
# ============================================================

def get_payments():

    return _make_request(
        "GET",
        f"{API_BASE_URL}/payments/",
        timeout=10
    )


# ============================================================
# GET SINGLE PAYMENT
# ============================================================

def get_payment(
    payment_id
):

    return _make_request(
        "GET",
        f"{API_BASE_URL}/payments/{payment_id}",
        timeout=10
    )


# ============================================================
# GET VALIDATION RESULTS
# ============================================================

def get_validation_results():

    return _make_request(
        "GET",
        f"{API_BASE_URL}/validation/",
        timeout=10
    )


# ============================================================
# UPLOAD PAYMENT XML
# ============================================================
def upload_payment_file(file):

    files = {
        "file": (
            file.name,
            file.getvalue(),
            file.type or "application/xml"
        )
    }

    return _make_request(
        "POST",
        f"{API_BASE_URL}/upload/",
        files=files,
        timeout=60
    )


# ============================================================
# GET ALL AUDIT LOGS
# ============================================================

def get_audit_logs():
    """
    Retrieve the complete audit trail.
    """

    return _make_request(
        "GET",
        f"{API_BASE_URL}/audit-logs/",
        timeout=10
    )


# ============================================================
# GET AUDIT LOGS FOR ONE PAYMENT
# ============================================================

def get_payment_audit_logs(
    payment_id
):
    """
    Retrieve the audit history for a specific payment.
    """

    return _make_request(
        "GET",
        f"{API_BASE_URL}/payments/{payment_id}/audit-logs",
        timeout=10
    )

def get_ai_rejections():
    """
    Retrieve AI-generated rejection analyses
    from the FastAPI backend.
    """

    return _make_request(
        "GET",
        f"{API_BASE_URL}/ai/rejections",
        timeout=10
    )