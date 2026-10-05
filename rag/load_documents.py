from pathlib import Path

from langchain_community.document_loaders import TextLoader


PROJECT_ROOT = Path(__file__).resolve().parent.parent

KNOWLEDGE_BASE = PROJECT_ROOT / "knowledge_base"


def load_documents():
    """
    Load all Markdown documents from the PayFlow
    Intelligence knowledge base.
    """

    documents = []

    markdown_files = sorted(
        KNOWLEDGE_BASE.rglob("*.md")
    )

    if not markdown_files:
        raise FileNotFoundError(
            "No Markdown documents found in the knowledge base."
        )

    for file_path in markdown_files:

        loader = TextLoader(
            str(file_path),
            encoding="utf-8"
        )

        loaded = loader.load()

        for document in loaded:

            relative_path = file_path.relative_to(
                PROJECT_ROOT
            )

            document.metadata.update(
                {
                    "source": str(relative_path),
                    "file_name": file_path.name,
                    "category": file_path.parent.name,
                    "file_type": file_path.suffix.lower(),
                }
            )

            documents.append(document)

    return documents
