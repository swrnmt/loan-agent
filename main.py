from agents.intake_agent import intake_agent
from agents.ocr_agent import ocr_agent
from agents.decision_agent import decision_agent

def run_pipeline(form_data: dict, pdf_bytes: bytes) -> dict:
    # Step 1: Structure the form input
    state = intake_agent(form_data)

    # Step 2: Extract income from PDF
    state = ocr_agent(state, pdf_bytes)

    # Step 3: Make a decision
    state = decision_agent(state)

    return state