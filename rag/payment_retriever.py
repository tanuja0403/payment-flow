from pathlib import Path
from typing import Any, Dict, List

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings


PROJECT_ROOT = Path(__file__).resolve().parent.parent

VECTOR_DB_PATH = PROJECT_ROOT / "data" / "chroma_db"

COLLECTION_NAME = "payflow_knowledge"

EMBEDDING_MODEL = "nomic-embed-text"


def get_vector_store() -> Chroma:
    """
    Load the existing PayFlow Chroma vector database.
    """

    embeddings = OllamaEmbeddings(
        model=EMBEDDING_MODEL
    )

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(VECTOR_DB_PATH),
    )

    return vector_store


def normalize_error(error: Any) -> Dict[str, str]:
    """
    Convert different validation-error formats into
    a consistent structure.
    """

    if isinstance(error, dict):
        return {
            "field": str(error.get("field", "")),
            "code": str(error.get("code", "")),
            "message": str(error.get("message", "")),
        }

    if isinstance(error, str):
        return {
            "field": "",
            "code": "",
            "message": error,
        }

    return {
        "field": "",
        "code": "",
        "message": str(error),
    }


def retrieve_for_error(
    error: Any,
    k: int = 4,
) -> List[Dict[str, Any]]:
    """
    Retrieve knowledge relevant to ONE validation error.
    """

    normalized = normalize_error(error)

    query_parts = [
        normalized["code"],
        normalized["field"],
        normalized["message"],
    ]

    query = " ".join(
        part for part in query_parts if part
    ).strip()

    if not query:
        return []

    vector_store = get_vector_store()

    documents = vector_store.similarity_search(
        query,
        k=k,
    )

    results = []

    for document in documents:
        results.append(
            {
                "content": document.page_content,
                "source": document.metadata.get(
                    "source",
                    "unknown",
                ),
                "category": document.metadata.get(
                    "category",
                    "unknown",
                ),
            }
        )

    return results


def retrieve_for_errors(
    errors: List[Any],
    k_per_error: int = 4,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Retrieve knowledge independently for every validation error.

    This is the important part that makes RAG dynamic.

    Example:

        MISSING_AMOUNT
              ↓
        amount knowledge

        MISSING_CURRENCY
              ↓
        currency knowledge

        MISSING_ACCOUNT
              ↓
        account knowledge
    """

    retrieved = {}

    for error in errors:

        normalized = normalize_error(error)

        code = normalized["code"] or (
            normalized["field"] or "UNKNOWN_ERROR"
        )

        retrieved[code] = retrieve_for_error(
            normalized,
            k=k_per_error,
        )

    return retrieved