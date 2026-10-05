from rag.rag_pipeline import generate_payment_analysis


validation_result = {
    "payment_id": "TEST-001",
    "status": "REJECTED",
    "errors": [
        {
            "field": "amount",
            "code": "MISSING_AMOUNT",
            "message": "Payment amount is missing."
        }
    ],
    "warnings": []
}


result = generate_payment_analysis(
    validation_result,
    k=4
)


print("\n" + "=" * 70)
print("PAYFLOW AI RESULT")
print("=" * 70)

print("\nVALIDATION ERROR")
print("-" * 70)

for error in validation_result["errors"]:
    print(f"Code    : {error['code']}")
    print(f"Field   : {error['field']}")
    print(f"Message : {error['message']}")

print("\nAI ANALYSIS")
print("-" * 70)

print(result["answer"])

print("\nKNOWLEDGE SOURCES")
print("-" * 70)

for source in result["sources"]:
    print(f"- {source}")

print("\n" + "=" * 70)
