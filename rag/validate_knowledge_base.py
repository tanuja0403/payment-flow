from pathlib import Path


KNOWLEDGE_BASE = Path(__file__).resolve().parent.parent / "knowledge_base"


def main():
    if not KNOWLEDGE_BASE.exists():
        print("ERROR: knowledge_base directory does not exist.")
        return

    files = sorted(KNOWLEDGE_BASE.rglob("*.md"))

    if not files:
        print("ERROR: No Markdown knowledge files found.")
        return

    print("=" * 60)
    print("PAYFLOW INTELLIGENCE - KNOWLEDGE BASE CHECK")
    print("=" * 60)

    valid = 0

    for file in files:
        content = file.read_text(encoding="utf-8").strip()

        relative_path = file.relative_to(KNOWLEDGE_BASE)

        if content:
            print(f"[OK] {relative_path} ({len(content)} characters)")
            valid += 1
        else:
            print(f"[EMPTY] {relative_path}")

    print("-" * 60)
    print(f"Documents found : {len(files)}")
    print(f"Valid documents  : {valid}")
    print("=" * 60)

    if valid != len(files):
        raise SystemExit("Knowledge base validation failed.")

    print("Knowledge base validation successful.")


if __name__ == "__main__":
    main()
