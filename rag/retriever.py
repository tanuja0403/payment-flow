from pathlib import Path

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings


PROJECT_ROOT = Path(__file__).resolve().parent.parent

VECTOR_DB_PATH = PROJECT_ROOT / "data" / "chroma_db"

COLLECTION_NAME = "payflow_knowledge"

EMBEDDING_MODEL = "nomic-embed-text"


def get_vector_store():

    embeddings = OllamaEmbeddings(
        model=EMBEDDING_MODEL
    )

    return Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(VECTOR_DB_PATH),
        embedding_function=embeddings,
    )


def retrieve(query, k=4):

    vector_store = get_vector_store()

    results = vector_store.similarity_search(
        query,
        k=k
    )

    return results


def main():

    print("=" * 60)
    print("PAYFLOW INTELLIGENCE - RAG RETRIEVAL")
    print("=" * 60)

    query = (
        "What should be done when the beneficiary "
        "address is missing?"
    )

    print(f"\nQuery:\n{query}\n")

    results = retrieve(query, k=4)

    print(f"Retrieved chunks: {len(results)}\n")

    for index, document in enumerate(results, start=1):

        print("-" * 60)
        print(f"RESULT {index}")

        print(
            f"Source: {document.metadata.get('source')}"
        )

        print(
            f"Category: {document.metadata.get('category')}"
        )

        print("\nContent:")
        print(document.page_content)

    print("\n" + "=" * 60)
    print("RETRIEVAL SUCCESSFUL")
    print("=" * 60)


if __name__ == "__main__":
    main()
