from rag.load_documents import load_documents
from rag.chunk_documents import chunk_documents
from langchain_ollama import OllamaEmbeddings


EMBEDDING_MODEL = "nomic-embed-text"


def create_embedding_model():
    return OllamaEmbeddings(
        model=EMBEDDING_MODEL
    )


def main():
    print("=" * 60)
    print("PAYFLOW INTELLIGENCE - EMBEDDINGS")
    print("=" * 60)

    documents = load_documents()
    chunks = chunk_documents(documents)

    print(f"Documents : {len(documents)}")
    print(f"Chunks    : {len(chunks)}")
    print()

    embeddings = create_embedding_model()

    test_text = chunks[0].page_content

    vector = embeddings.embed_query(test_text)

    print(f"Embedding model : {EMBEDDING_MODEL}")
    print(f"Vector size     : {len(vector)}")
    print()
    print("Embedding generation successful.")

    print("=" * 60)


if __name__ == "__main__":
    main()
