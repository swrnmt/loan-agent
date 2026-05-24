from langgraph.graph import StateGraph, END
from state.loan_state import LoanState
from agents.intake_agent import intake_agent
from agents.ocr_agent import ocr_agent
from agents.verification_agent import verification_agent
from agents.risk_agent import risk_agent
from agents.fraud_agent import fraud_agent
from agents.decision_agent import decision_agent
from agents.report_agent import report_agent

def build_graph():
    graph = StateGraph(LoanState)

    graph.add_node("ocr", ocr_agent)
    graph.add_node("verification", verification_agent)
    graph.add_node("risk", risk_agent)
    graph.add_node("fraud", fraud_agent)
    graph.add_node("decision", decision_agent)
    graph.add_node("report", report_agent)

    graph.set_entry_point("ocr")
    graph.add_edge("ocr", "verification")
    graph.add_edge("verification", "risk")
    graph.add_edge("risk", "fraud")
    graph.add_edge("fraud", "decision")
    graph.add_edge("decision", "report")
    graph.add_edge("report", END)

    return graph.compile()

def run_pipeline(form_data: dict, pdf_bytes: bytes) -> dict:
    initial_state = intake_agent(form_data, pdf_bytes)
    initial_state["report_pdf"] = None
    app = build_graph()
    final_state = app.invoke(initial_state)
    return final_state