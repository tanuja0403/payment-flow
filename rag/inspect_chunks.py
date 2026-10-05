from rag.load_documents import load_documents
from rag.chunk_documents import chunk_documents


def main():

    documents = load_documents()
    chunks = chunk_documents(documents)

    print("=" * 70)
    print("PAYFLOW INTELLIGENCE - CHUNK INSPECTOR")
    print("=" * 70)

    for index, chunk in enumerate(chunks):

        print()
        print("#" * 70)

        print(f"CHUNK {index}")

        print(
            f"Source   : {chunk.metadata.get('source')}"
        )

        print(
            f"Category : {chunk.metadata.get('category')}"
        )

        print(
            f"Size     : {len(chunk.page_content)}"
        )

        print("#" * 70)

        print(chunk.page_content)


if __name__ == "__main__":
    main()
