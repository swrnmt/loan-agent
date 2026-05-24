from state.loan_state import LoanState

def decision_agent(state: LoanState) -> LoanState:
    employment = state["employment_type"]
    risk_tier = state["risk_tier"]
    fraud_score = state["fraud_score"]
    verification_confidence = state["verification_confidence"]

    # Check employment type first — hard rejection, no escalation
    if employment != "salaried":
        state["decision"] = "Rejected"
        state["reason"] = "Only salaried applicants are eligible."
        return state

    # Escalate to manual review if fraud score is high
    if fraud_score >= 0.6:
        state["decision"] = "Manual Review"
        state["reason"] = f"High fraud score of {fraud_score:.0%}. Flags: {', '.join(state['fraud_flags'])}"
        return state

    # Escalate if verification confidence is too low
    if verification_confidence <= 0.5:
        state["decision"] = "Manual Review"
        state["reason"] = f"Low verification confidence. Flags: {', '.join(state['verification_flags'])}"
        return state

    # Decision based on risk tier
    if risk_tier == "Low":
        state["decision"] = "Approved"
        state["reason"] = f"Low risk. EMI burden is {state['emi_burden_pct']}% of income."
    elif risk_tier == "Medium":
        state["decision"] = "Approved"
        state["reason"] = f"Medium risk. EMI burden is {state['emi_burden_pct']}% of income. Approved with caution."
    else:
        state["decision"] = "Rejected"
        state["reason"] = f"High risk. EMI burden is {state['emi_burden_pct']}% of income, exceeding 50% threshold."

    return state