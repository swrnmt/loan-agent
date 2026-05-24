from langgraph.graph import StateGraph, END
from state.loan_state import LoanState
from agents.intake_agent import intake_agent
from agents.ocr_agent import ocr_agent
from agents.decision_agent import decision_agent

# Build the graph
def build_graph():
    graph = StateGraph(LoanState)

    # Add each agent as a node
    graph.add_node("ocr", ocr_agent)
    graph.add_node("decision", decision_agent)

    # Define the flow: ocr -> decision -> end
    graph.set_entry_point("ocr")
    graph.add_edge("ocr", "decision")
    graph.add_edge("decision", END)

    return graph.compile()

# Run the full pipeline
def run_pipeline(form_data: dict, pdf_bytes: bytes) -> dict:
    # Intake agent creates the initial state (outside the graph)
    initial_state = intake_agent(form_data, pdf_bytes)

    # LangGraph takes over from here
    app = build_graph()
    final_state = app.invoke(initial_state)

    return final_state