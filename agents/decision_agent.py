from state.loan_state import LoanState

def decision_agent(state: LoanState) -> LoanState:
    income = state["ocr_extracted_income"] or state["stated_income"]
    loan_amount = state["loan_amount"]
    tenure = state["loan_tenure_months"]
    employment = state["employment_type"]

    # Calculate EMI using simple flat rate (we'll use proper formula in Phase 2)
    # EMI = loan_amount / tenure (simplified for Phase 1)
    emi = round(loan_amount / tenure, 2)
    state["emi"] = emi

    # Rule: income must be at least 3x the EMI, and applicant must be salaried
    if employment == "salaried" and income >= 3 * emi:
        state["decision"] = "Approved"
        state["reason"] = f"Income of ₹{income:,.0f} is sufficient for EMI of ₹{emi:,.0f}."
    elif employment != "salaried":
        state["decision"] = "Rejected"
        state["reason"] = "Only salaried applicants are eligible in Phase 1."
    else:
        state["decision"] = "Rejected"
        state["reason"] = f"Income of ₹{income:,.0f} is less than 3x EMI of ₹{emi:,.0f}."

    return state