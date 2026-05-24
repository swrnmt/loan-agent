from state.loan_state import LoanState

def fraud_agent(state: LoanState) -> LoanState:
    """
    Detects suspicious patterns in the application.
    """
    flags = []
    fraud_score = 0.0

    stated = state["stated_income"]
    extracted = state["ocr_extracted_income"]
    mismatch_pct = state.get("income_mismatch_pct")

    # Flag 1: Large income mismatch
    if mismatch_pct and mismatch_pct > 20:
        flags.append(f"Large income mismatch of {mismatch_pct:.1f}%")
        fraud_score += 0.4

    # Flag 2: Suspiciously round income figure
    if stated % 10000 == 0:
        flags.append("Stated income is a suspiciously round number")
        fraud_score += 0.2

    # Flag 3: OCR income much lower than stated
    if extracted and extracted < stated * 0.7:
        flags.append("OCR income is significantly lower than stated income")
        fraud_score += 0.3

    # Cap fraud score at 1.0
    fraud_score = min(round(fraud_score, 2), 1.0)

    state["fraud_flags"] = flags
    state["fraud_score"] = fraud_score

    return state