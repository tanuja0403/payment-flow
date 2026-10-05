from pathlib import Path

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

from rag.load_documents import load_documents
from rag.chunk_documents import chunk_documents


PROJECT_ROOT = Path(__file__).resolve().parent.parent

VECTOR_DB_PATH = PROJECT_ROOT / "data" / "chroma_db"

COLLECTION_NAME = "payflow_knowledge"

EMBEDDING_MODEL = "nomic-embed-text"


def create_vector_store():

    documents = load_documents()
    chunks = chunk_documents(documents)

    embeddings = OllamaEmbeddings(
        model=EMBEDDING_MODEL
    )

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=str(VECTOR_DB_PATH),
    )

    return vector_store, chunks


def main():

    print("=" * 60)
    print("PAYFLOW INTELLIGENCE - VECTOR DATABASE")
    print("=" * 60)

    vector_store, chunks = create_vector_store()

    print(f"Chunks stored : {len(chunks)}")
    print(f"Database      : {VECTOR_DB_PATH}")
    print(f"Collection    : {COLLECTION_NAME}")

    print()
    print("Vector database created successfully.")

    print("=" * 60)


if __name__ == "__main__":
    main()
