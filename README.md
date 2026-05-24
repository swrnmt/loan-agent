# Loan Application Processing Agent

An end-to-end agentic AI system that automates loan application processing for BFSI (Banking, Financial Services & Insurance).

## Live Demo
https://loan-agent.streamlit.app

## What it does
- Accepts applicant details via a Streamlit form
- Extracts income from uploaded salary slip PDF using OCR
- Verifies stated income against OCR-extracted income
- Computes debt-to-income ratio and assigns a risk tier
- Detects fraud patterns and assigns a fraud score
- Outputs Approved / Rejected / Manual Review with full reasoning
- Generates a downloadable PDF audit report with LLM-written officer notes
- Stores all applications in a database with timestamps

## Agent Architecture

| Agent | Responsibility |
|-------|---------------|
| Intake Agent | Structures form input into shared LangGraph state |
| OCR Agent | Extracts income from PDF using PyMuPDF + Tesseract |
| Verification Agent | Cross-checks stated vs extracted income, flags mismatches above 15% |
| Risk Agent | Computes DTI ratio, EMI burden, assigns Low / Medium / High risk tier |
| Fraud Agent | Detects suspicious patterns, outputs fraud score 0 to 1 |
| Decision Agent | Combines risk tier and fraud score, outputs decision with reason codes |
| Report Agent | Generates downloadable PDF audit report with Groq LLM officer notes |

## Key Design Decisions
- No agent makes a final decision alone
- Human escalation triggered when fraud score is above 0.6 or verification confidence is below 0.5
- Every decision includes reason codes, not just approve or reject
- LLM outputs validated against structured schemas before passing to next agent
- Employment type check happens before fraud check to ensure correct rejection path
- Database schema tracks all agent outputs including risk tier, fraud score, and verification confidence

## Tech Stack

| Layer | Tool |
|-------|------|
| Orchestration | LangGraph |
| LLM | Groq API (Llama 3.3 70B) |
| OCR | PyMuPDF + Tesseract |
| Backend | FastAPI |
| Database | SQLite + SQLAlchemy |
| UI | Streamlit |
| Reports | ReportLab |
| Deployment | Streamlit Cloud |

## Project Structure
```
loan-agent/
├── agents/
│   ├── intake_agent.py        # Structures form input into state
│   ├── ocr_agent.py           # Extracts income from PDF
│   ├── verification_agent.py  # Cross-checks income figures
│   ├── risk_agent.py          # Computes risk tier
│   ├── fraud_agent.py         # Detects fraud patterns
│   ├── decision_agent.py      # Makes final decision
│   └── report_agent.py        # Generates PDF audit report
├── state/
│   └── loan_state.py          # Shared state object (TypedDict)
├── app.py                     # Streamlit UI
├── main.py                    # LangGraph pipeline
├── database.py                # SQLite storage
├── test_profiles.py           # 10 profile simulation test
├── packages.txt               # System dependencies for Streamlit Cloud
└── requirements.txt
```
## How to run locally

```bash
# Install dependencies
pip install -r requirements.txt

# Install Tesseract OCR binary
# Windows: https://github.com/UB-Mannheim/tesseract/wiki
# Mac: brew install tesseract
# Linux: sudo apt install tesseract-ocr

# Set Groq API key
export GROQ_API_KEY=your_key_here
# On Windows PowerShell:
# $env:GROQ_API_KEY="your_key_here"

# Run the app
streamlit run app.py
```

## Test Profiles
Run the automated test suite with 10 simulated profiles:
```bash
python test_profiles.py
```

Expected results: 5 Approved, 3 Manual Review, 2 Rejected

## Decision Logic

| Condition | Decision |
|-----------|---------|
| Employment is self-employed | Rejected |
| Fraud score above 0.6 | Manual Review |
| Verification confidence below 0.5 | Manual Review |
| EMI burden below 30% of income | Approved (Low Risk) |
| EMI burden between 30% and 50% | Approved with caution (Medium Risk) |
| EMI burden above 50% | Rejected (High Risk) |

## Interview Talking Points

**The Problem:** Loan processing in Indian banks is still semi-manual. KYC verification, income checks, and risk scoring involve multiple teams, multiple documents, and multiple days.

**The Architecture:** Seven specialized agents, each with one job. LangGraph manages state transitions between them. Every decision is explainable — the system tells you why it decided, not just what it decided.

**The Hard Part:** Hallucination control. An LLM saying a loan is approved when it should not be is a serious problem in banking. Every LLM output is validated against a structured schema before passing to the next agent, and confidence thresholds trigger human escalation instead of autonomous high-stakes decisions.

**The Result:** A fully deployed system that processes a simulated loan application end-to-end in under 30 seconds — including OCR extraction, income verification, fraud detection, risk scoring, and PDF report generation with LLM-written officer notes.