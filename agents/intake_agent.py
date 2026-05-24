from state.loan_state import LoanState

def intake_agent(data: dict) -> LoanState:
    state: LoanState = {
        "applicant_name": data["applicant_name"],
        "stated_income": float(data["stated_income"]),
        "loan_amount": float(data["loan_amount"]),
        "loan_tenure_months": int(data["loan_tenure_months"]),
        "employment_type": data["employment_type"],
        "ocr_extracted_income": None,
        "ocr_confidence": None,
        "emi": None,
        "decision": None,
        "reason": None,
    }
    return state