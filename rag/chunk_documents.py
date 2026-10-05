from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag.load_documents import load_documents



# ---------------------------------------------------------
# CHUNKING CONFIGURATION
# ---------------------------------------------------------

CHUNK_SIZE = 700
CHUNK_OVERLAP = 100


# ---------------------------------------------------------
# CREATE TEXT SPLITTER
# ---------------------------------------------------------

def create_text_splitter():
    """
    Create the text splitter used by the PayFlow
    Intelligence RAG pipeline.
    """

    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=[
            "\n## ",
            "\n### ",
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ],
    )


# ---------------------------------------------------------
# SPLIT DOCUMENTS
# ---------------------------------------------------------

def chunk_documents(documents):
    """
    Split LangChain Documents into smaller chunks.
    """

    splitter = create_text_splitter()

    chunks = splitter.split_documents(documents)

    # Add chunk-specific metadata.
    for index, chunk in enumerate(chunks):

        chunk.metadata["chunk_id"] = index

        chunk.metadata["chunk_size"] = len(
            chunk.page_content
        )

    return chunks


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    print("=" * 70)
    print("PAYFLOW INTELLIGENCE - RAG CHUNKING")
    print("=" * 70)

    # Load original documents.
    documents = load_documents()

    print(f"Original documents : {len(documents)}")

    # Split documents.
    chunks = chunk_documents(documents)

    print(f"Generated chunks   : {len(chunks)}")
    print()

    print("-" * 70)

    for index, chunk in enumerate(chunks[:10]):

        print(f"\nCHUNK #{index}")

        print(
            f"Source: {chunk.metadata.get('source')}"
        )

        print(
            f"Category: {chunk.metadata.get('category')}"
        )

        print(
            f"Characters: {len(chunk.page_content)}"
        )

        print("\nContent:")
        print(chunk.page_content[:500])

        print("-" * 70)

    print()
    print("=" * 70)
    print("CHUNKING SUCCESSFUL")
    print("=" * 70)


if __name__ == "__main__":
    main()
