from load_documents import load_documents


def main():

    documents = load_documents()

    print("=" * 60)
    print("LANGCHAIN DOCUMENT LOADER TEST")
    print("=" * 60)

    print(f"Total documents: {len(documents)}")
    print()

    for index, document in enumerate(documents, start=1):

        print(f"[{index}]")

        print(
            "Source:",
            document.metadata["source"]
        )

        print(
            "Category:",
            document.metadata["category"]
        )

        print(
            "Characters:",
            len(document.page_content)
        )

        print()


if __name__ == "__main__":
    main()
