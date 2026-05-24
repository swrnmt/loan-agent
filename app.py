import streamlit as st
from main import run_pipeline
from database import init_db, save_application, get_all_applications

init_db()

st.set_page_config(page_title="Loan Application Agent", page_icon="🏦", layout="centered")

# --- Session State ---
if "result" not in st.session_state:
    st.session_state.result = None
if "screen" not in st.session_state:
    st.session_state.screen = "form"
if "show_about" not in st.session_state:
    st.session_state.show_about = False
if "show_history" not in st.session_state:
    st.session_state.show_history = False

# =====================
# SCREEN 1: FORM
# =====================
if st.session_state.screen == "form":

    # --- Header ---
    col_title, col_about = st.columns([5, 1])
    with col_title:
        st.markdown("## 🏦 Loan Application Agent")
    with col_about:
        if st.button("About"):
            st.session_state.show_about = not st.session_state.show_about

    if st.session_state.show_about:
        st.info("""
**What is this?**
An agentic AI system that automates loan application processing end to end — the kind of system banks are actually deploying right now.

**7 agents, one pipeline:**
1. Intake Agent — structures your form input
2. OCR Agent — reads income from your salary slip PDF
3. Verification Agent — cross-checks stated vs extracted income
4. Risk Agent — computes debt-to-income ratio and risk tier
5. Fraud Agent — detects suspicious patterns
6. Decision Agent — approves, rejects, or escalates to human review
7. Report Agent — generates a PDF audit report with AI-written officer notes

**Built with:** LangGraph, Groq (Llama 3.3 70B), Tesseract OCR, SQLite, Streamlit
        """)

    st.divider()
    st.markdown("### Applicant Details")

    col1, col2 = st.columns(2)
    with col1:
        applicant_name = st.text_input("Full Name")
        stated_income = st.number_input("Monthly Income (₹)", min_value=0.0, step=1000.0)
        loan_amount = st.number_input("Loan Amount Requested (₹)", min_value=0.0, step=10000.0)
    with col2:
        loan_tenure_months = st.selectbox("Loan Tenure", [12, 24, 36, 48, 60], index=2)
        employment_type = st.selectbox("Employment Type", ["salaried", "self-employed"])
        uploaded_file = st.file_uploader("Upload Salary Slip (PDF)", type=["pdf"])

    st.markdown("")

    if st.button("🚀 Submit Application", use_container_width=True):
        errors = []
        if not applicant_name or len(applicant_name.strip()) < 2:
            errors.append("Please enter a valid full name.")
        if stated_income <= 0:
            errors.append("Monthly income must be greater than 0.")
        if loan_amount <= 0:
            errors.append("Loan amount must be greater than 0.")
        if loan_amount > 50000000:
            errors.append("Loan amount cannot exceed ₹5 crore.")
        if not uploaded_file:
            errors.append("Please upload your salary slip PDF.")

        if errors:
            for error in errors:
                st.error(error)
        else:
            try:
                progress = st.progress(0, text="Starting pipeline...")
                status = st.empty()

                status.text("📋 Intake Agent — structuring form data...")
                progress.progress(10)
                status.text("🔍 OCR Agent — extracting income from PDF...")
                progress.progress(25)
                status.text("✅ Verification Agent — cross-checking income...")
                progress.progress(40)
                status.text("📊 Risk Agent — computing debt-to-income ratio...")
                progress.progress(55)
                status.text("🚨 Fraud Agent — checking for suspicious patterns...")
                progress.progress(70)
                status.text("⚖️ Decision Agent — making final decision...")
                progress.progress(85)

                form_data = {
                    "applicant_name": applicant_name.strip(),
                    "stated_income": stated_income,
                    "loan_amount": loan_amount,
                    "loan_tenure_months": loan_tenure_months,
                    "employment_type": employment_type,
                }
                pdf_bytes = uploaded_file.read()
                result = run_pipeline(form_data, pdf_bytes)
                save_application(result)

                status.text("📄 Report Agent — generating audit report...")
                progress.progress(95)
                progress.progress(100, text="Done!")
                status.empty()
                progress.empty()

                st.session_state.result = result
                st.session_state.screen = "result"
                st.rerun()

            except Exception as e:
                st.error("Something went wrong. Please try again.")
                st.exception(e)

    # --- Application History ---
    st.divider()
    col_hist, col_toggle = st.columns([5, 1])
    with col_hist:
        st.markdown("### Application History")
    with col_toggle:
        if st.button("Show" if not st.session_state.show_history else "Hide"):
            st.session_state.show_history = not st.session_state.show_history

    if st.session_state.show_history:
        records = get_all_applications()
        if records:
            history = []
            for r in records:
                if r.decision == "Approved":
                    badge = "🟢 Approved"
                elif r.decision == "Manual Review":
                    badge = "🟡 Manual Review"
                else:
                    badge = "🔴 Rejected"
                history.append({
                    "Name": r.applicant_name,
                    "Income": f"₹{r.stated_income:,.0f}",
                    "Loan": f"₹{r.loan_amount:,.0f}",
                    "EMI": f"₹{r.emi:,.0f}" if r.emi else "-",
                    "Risk": r.risk_tier if r.risk_tier else "-",
                    "Fraud": f"{r.fraud_score:.0%}" if r.fraud_score is not None else "-",
                    "Decision": badge,
                    "Time": r.created_at.strftime("%d %b, %H:%M")
                })
            st.dataframe(history, use_container_width=True)
        else:
            st.info("No applications submitted yet.")

# =====================
# SCREEN 2: RESULT
# =====================
elif st.session_state.screen == "result":
    result = st.session_state.result

    if st.button("← Back to Form"):
        st.session_state.screen = "form"
        st.session_state.result = None
        st.rerun()

    st.markdown("### Application Result")

    if result["decision"] == "Approved":
        st.success(f"✅ **{result['decision']}**")
    elif result["decision"] == "Manual Review":
        st.warning(f"⚠️ **{result['decision']} Required**")
    else:
        st.error(f"❌ **{result['decision']}**")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Monthly EMI", f"₹{result['emi']:,.0f}")
    with col2:
        st.metric("Risk Tier", result["risk_tier"])
    with col3:
        st.metric("Fraud Score", f"{result['fraud_score']:.0%}")

    st.markdown(f"**Reason:** {result['reason']}")
    if result["ocr_extracted_income"]:
        st.markdown(f"**OCR Extracted Income:** ₹{result['ocr_extracted_income']:,.0f}")
    else:
        st.markdown("**OCR Extracted Income:** Could not extract — using stated income.")

    st.markdown("### Audit Trail")

    st.markdown(f"**Intake Agent:** Received application from {result['applicant_name']}. "
                f"Stated income ₹{result['stated_income']:,.0f}, "
                f"loan request ₹{result['loan_amount']:,.0f} over {result['loan_tenure_months']} months.")

    if result["ocr_extracted_income"]:
        st.markdown(f"**OCR Agent:** Extracted income of ₹{result['ocr_extracted_income']:,.0f} "
                    f"from salary slip (confidence: {result['ocr_confidence']:.0%}).")
    else:
        st.markdown("**OCR Agent:** Could not extract income. Falling back to stated income.")

    if result["income_match"]:
        st.markdown(f"**Verification Agent:** Income verified. "
                    f"Mismatch within {result['income_mismatch_pct']:.1f}%. "
                    f"Confidence: {result['verification_confidence']:.0%}.")
    else:
        flags = ", ".join(result["verification_flags"]) if result["verification_flags"] else "None"
        st.markdown(f"**Verification Agent:** Income mismatch detected. "
                    f"Mismatch: {result['income_mismatch_pct']:.1f}%. "
                    f"Flags: {flags}. Confidence: {result['verification_confidence']:.0%}.")

    st.markdown(f"**Risk Agent:** Debt-to-income ratio: {result['debt_to_income_ratio']:.2f}. "
                f"EMI burden: {result['emi_burden_pct']:.1f}% of income. "
                f"Risk tier: **{result['risk_tier']}**.")

    if result["fraud_flags"]:
        flags = ", ".join(result["fraud_flags"])
        st.markdown(f"**Fraud Agent:** {len(result['fraud_flags'])} flag(s) detected. "
                    f"Fraud score: {result['fraud_score']:.0%}. Flags: {flags}.")
    else:
        st.markdown(f"**Fraud Agent:** No suspicious patterns detected. "
                    f"Fraud score: {result['fraud_score']:.0%}.")

    st.markdown(f"**Decision Agent:** Final decision: **{result['decision']}**. {result['reason']}")

    if result.get("report_pdf"):
        st.download_button(
            label="📄 Download Audit Report (PDF)",
            data=result["report_pdf"],
            file_name=f"loan_report_{result['applicant_name'].replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    with st.expander("See full application state"):
        display_state = {k: v for k, v in result.items() if k != "pdf_bytes" and k != "report_pdf"}
        st.json(display_state)