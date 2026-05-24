from state.loan_state import LoanState

def risk_agent(state: LoanState) -> LoanState:
    """
    Computes debt-to-income ratio, EMI burden percentage,
    and assigns a risk tier.
    """
    income = state["ocr_extracted_income"] or state["stated_income"]
    loan_amount = state["loan_amount"]
    tenure = state["loan_tenure_months"]

    # EMI calculation
    emi = round(loan_amount / tenure, 2)
    state["emi"] = emi

    # Debt to income ratio: EMI as a fraction of monthly income
    dti = round(emi / income, 4) if income > 0 else 1.0
    state["debt_to_income_ratio"] = dti

    # EMI burden as a percentage
    emi_burden = round(dti * 100, 2)
    state["emi_burden_pct"] = emi_burden

    # Assign risk tier based on EMI burden
    if emi_burden <= 30:
        state["risk_tier"] = "Low"
    elif emi_burden <= 50:
        state["risk_tier"] = "Medium"
    else:
        state["risk_tier"] = "High"

    return state