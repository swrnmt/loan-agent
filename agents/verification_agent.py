from state.loan_state import LoanState

def verification_agent(state: LoanState) -> LoanState:
    """
    Cross-checks stated income vs OCR extracted income.
    Flags mismatches above 15%.
    """
    stated = state["stated_income"]
    extracted = state["ocr_extracted_income"]
    flags = []

    if extracted is None:
        # OCR failed, can't verify
        state["income_match"] = False
        state["income_mismatch_pct"] = None
        state["verification_flags"] = ["OCR extraction failed - cannot verify income"]
        state["verification_confidence"] = 0.4
        return state

    # Calculate how different the two income figures are
    mismatch_pct = abs(stated - extracted) / max(stated, extracted) * 100

    if mismatch_pct > 15:
        flags.append(f"Income mismatch of {mismatch_pct:.1f}% — stated ₹{stated:,.0f} vs extracted ₹{extracted:,.0f}")
        income_match = False
        confidence = 0.5
    else:
        income_match = True
        confidence = 0.9

    state["income_match"] = income_match
    state["income_mismatch_pct"] = round(mismatch_pct, 2)
    state["verification_flags"] = flags
    state["verification_confidence"] = confidence

    return state