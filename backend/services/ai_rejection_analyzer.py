"""
AI Rejection Analyzer
----------------------

Phase 10:
Uses Ollama locally to analyze rejected payments.

No OpenAI API is required.
"""

import json
from typing import Any, Dict

try:
    import ollama
except ImportError:
    ollama = None


# =========================================================
# CONFIGURATION
# =========================================================

# IMPORTANT:
# Ollama lists the model as "llama3.2:latest",
# but we use "llama3.2" when calling the model.
OLLAMA_MODEL = "llama3.2"

OLLAMA_HOST = "http://127.0.0.1:11434"


# =========================================================
# OLLAMA CONNECTION
# =========================================================

def _get_ollama_client():
    """
    Create an Ollama client connected to the local Ollama server.
    """

    if ollama is None:
        raise RuntimeError("Ollama Python package is not installed.")

    return ollama.Client(host=OLLAMA_HOST)


def _call_ollama(prompt: str) -> str:
    """
    Send a prompt to the locally running Ollama model.
    """

    try:

        client = _get_ollama_client()

        response = client.chat(
            model=OLLAMA_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a financial payment analysis assistant. "
                        "Analyze ISO 20022 payment validation failures. "
                        "Do not invent payment data. "
                        "Base your analysis only on the information provided. "
                        "Return only valid JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            format="json",
        )

        # Handle normal dictionary response
        if isinstance(response, dict):

            message = response.get("message", {})

            if isinstance(message, dict):
                content = message.get("content", "")

                if content:
                    return str(content)

        # Handle newer typed Ollama response objects
        if hasattr(response, "message"):

            message = response.message

            if hasattr(message, "content"):
                return str(message.content)

        raise RuntimeError(
            "Ollama returned an empty response."
        )

    except Exception as error:

        raise RuntimeError(
            f"Ollama request failed: {error}"
        ) from error


# =========================================================
# BUILD AI PROMPT
# =========================================================

def _build_prompt(
    payment: Dict[str, Any],
    validation_result: Dict[str, Any],
) -> str:
    """
    Build the prompt sent to Ollama.
    """

    payment_json = json.dumps(
        payment,
        indent=2,
        default=str,
    )

    validation_json = json.dumps(
        validation_result,
        indent=2,
        default=str,
    )

    prompt = f"""
Analyze the following ISO 20022 payment validation result.

PAYMENT DATA:
{payment_json}

VALIDATION RESULT:
{validation_json}

Determine:

1. Whether the payment is rejected or accepted.
2. The main rejection reason.
3. The root cause.
4. The severity.
5. Which field caused the problem.
6. How the problem can be fixed.
7. A short explanation for a human payment analyst.

IMPORTANT:
- Use ONLY the information provided.
- Do not invent missing payment information.
- If a field is unknown, say "Unknown".
- Return ONLY valid JSON.
- Do not use Markdown.
- Do not add text before or after the JSON.

Use exactly this structure:

{{
    "status": "REJECTED",
    "rejection_reason": "string",
    "root_cause": "string",
    "severity": "LOW",
    "problematic_field": "string",
    "recommendation": "string",
    "explanation": "string"
}}
"""

    return prompt


# =========================================================
# PARSE AI RESPONSE
# =========================================================

def _parse_ai_response(
    response_text: str,
) -> Dict[str, Any]:
    """
    Convert Ollama's response into a Python dictionary.
    """

    if not response_text:
        return {
            "status": "REJECTED",
            "rejection_reason": "Empty AI response",
            "root_cause": "Ollama returned no analysis",
            "severity": "MEDIUM",
            "problematic_field": "Unknown",
            "recommendation": "Review the validation result manually.",
            "explanation": "The local AI model returned an empty response.",
        }

    response_text = response_text.strip()

    # -----------------------------------------------------
    # Remove Markdown JSON fences
    # -----------------------------------------------------

    if response_text.startswith("```json"):

        response_text = response_text[len("```json"):]

    elif response_text.startswith("```"):

        response_text = response_text[len("```"):]

    if response_text.endswith("```"):

        response_text = response_text[:-3]

    response_text = response_text.strip()

    # -----------------------------------------------------
    # Parse JSON
    # -----------------------------------------------------

    try:

        result = json.loads(response_text)

    except json.JSONDecodeError:

        return {
            "status": "REJECTED",
            "rejection_reason": "AI returned an unstructured response",
            "root_cause": "Unable to parse AI response",
            "severity": "MEDIUM",
            "problematic_field": "Unknown",
            "recommendation": "Review the validation result manually.",
            "explanation": response_text,
        }

    # -----------------------------------------------------
    # Make sure result is a dictionary
    # -----------------------------------------------------

    if not isinstance(result, dict):

        return {
            "status": "REJECTED",
            "rejection_reason": "Invalid AI response format",
            "root_cause": "AI response was not a JSON object",
            "severity": "MEDIUM",
            "problematic_field": "Unknown",
            "recommendation": "Review the validation result manually.",
            "explanation": response_text,
        }

    # -----------------------------------------------------
    # Ensure all expected fields exist
    # -----------------------------------------------------

    result.setdefault(
        "status",
        "REJECTED",
    )

    result.setdefault(
        "rejection_reason",
        "Unknown",
    )

    result.setdefault(
        "root_cause",
        "Unknown",
    )

    result.setdefault(
        "severity",
        "MEDIUM",
    )

    result.setdefault(
        "problematic_field",
        "Unknown",
    )

    result.setdefault(
        "recommendation",
        "Review the validation result manually.",
    )

    result.setdefault(
        "explanation",
        "No explanation provided.",
    )

    return result


# =========================================================
# MAIN ANALYZER
# =========================================================

def analyze_rejection(
    payment: Dict[str, Any],
    validation_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Analyze a payment rejection using Ollama.

    Parameters
    ----------
    payment:
        Payment information extracted from ISO 20022.

    validation_result:
        Result produced by the validation engine.

    Returns
    -------
    dict
        AI-generated rejection analysis.
    """

    prompt = _build_prompt(
        payment,
        validation_result,
    )

    ai_response = _call_ollama(
        prompt
    )

    result = _parse_ai_response(
        ai_response
    )

    return result


# =========================================================
# OLLAMA HEALTH CHECK
# =========================================================
def check_ollama() -> Dict[str, Any]:
    """
    Check Ollama directly through its HTTP API.
    """

    try:
        import requests

        response = requests.get(
            "http://127.0.0.1:11434/api/tags",
            timeout=5
        )

        response.raise_for_status()

        data = response.json()

        model_names = []

        for model in data.get("models", []):
            name = model.get("name")

            if name:
                model_names.append(name)

        model_available = any(
            name == "llama3.2"
            or name == "llama3.2:latest"
            or name.startswith("llama3.2:")
            for name in model_names
        )

        return {
            "status": "success",
            "ollama_running": True,
            "model": "llama3.2",
            "model_available": model_available,
            "installed_models": model_names,
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


# =========================================================
# SIMPLE MODEL TEST
# =========================================================

def test_ollama() -> Dict[str, Any]:
    """
    Simple test to verify that the configured
    Ollama model can actually generate a response.
    """

    try:

        client = _get_ollama_client()

        response = client.chat(
            model=OLLAMA_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Reply with exactly this word: "
                        "OLLAMA_WORKING"
                    ),
                }
            ],
        )

        if isinstance(response, dict):

            message = response.get(
                "message",
                {}
            )

            if isinstance(message, dict):

                content = message.get(
                    "content",
                    ""
                )

            else:

                content = ""

        elif hasattr(response, "message"):

            message = response.message

            content = getattr(
                message,
                "content",
                ""
            )

        else:

            content = ""

        return {
            "status": "success",
            "model": OLLAMA_MODEL,
            "response": content,
        }

    except Exception as error:

        return {
            "status": "error",
            "model": OLLAMA_MODEL,
            "error": str(error),
        }