from pathlib import Path

from langchain_community.document_loaders import TextLoader


# ---------------------------------------------------------
# PATH CONFIGURATION
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

KNOWLEDGE_BASE = PROJECT_ROOT / "knowledge_base"


# ---------------------------------------------------------
# DOCUMENT LOADER
# ---------------------------------------------------------

def load_markdown_documents():
    """
    Load all Markdown files from the knowledge base.

    Each Markdown file is converted into LangChain
    Document objects.
    """

    documents = []

    markdown_files = sorted(KNOWLEDGE_BASE.rglob("*.md"))

    if not markdown_files:
        raise FileNotFoundError(
            f"No Markdown files found in {KNOWLEDGE_BASE}"
        )

    for file_path in markdown_files:

        loader = TextLoader(
            str(file_path),
            encoding="utf-8"
        )

        loaded_documents = loader.load()

        for document in loaded_documents:

            # Add useful metadata for future RAG retrieval.
            document.metadata.update(
                {
                    "source": str(
                        file_path.relative_to(PROJECT_ROOT)
                    ),
                    "file_name": file_path.name,
                    "category": file_path.parent.name,
                    "file_type": "markdown",
                }
            )

            documents.append(document)

    return documents


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    print("=" * 70)
    print("PAYFLOW INTELLIGENCE - RAG DOCUMENT INGESTION")
    print("=" * 70)

    print(f"Knowledge Base: {KNOWLEDGE_BASE}")
    print()

    documents = load_markdown_documents()

    print(f"Documents loaded: {len(documents)}")
    print()

    for index, document in enumerate(documents, start=1):

        print("-" * 70)

        print(f"Document #{index}")

        print(
            f"Source: {document.metadata.get('source')}"
        )

        print(
            f"Category: {document.metadata.get('category')}"
        )

        print(
            f"Characters: {len(document.page_content)}"
        )

        preview = (
            document.page_content
            .replace("\n", " ")
            .strip()
        )

        if len(preview) > 200:
            preview = preview[:200] + "..."

        print(f"Preview: {preview}")

    print()
    print("=" * 70)
    print("DOCUMENT INGESTION SUCCESSFUL")
    print("=" * 70)


if __name__ == "__main__":
    main()
