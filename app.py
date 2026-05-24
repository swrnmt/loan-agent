import streamlit as st
from main import run_pipeline
from database import init_db, save_application, get_all_applications

init_db()

st.set_page_config(page_title="Loan Application Agent", page_icon="🏦")

st.title("🏦 Loan Application Processing Agent")
st.markdown("Fill in your details and upload your salary slip to get an instant decision.")

# --- Form Section ---
st.subheader("Applicant Details")

applicant_name = st.text_input("Full Name")
stated_income = st.number_input("Monthly Income (₹)", min_value=0.0, step=1000.0)
loan_amount = st.number_input("Loan Amount Requested (₹)", min_value=0.0, step=10000.0)
loan_tenure_months = st.selectbox("Loan Tenure", [12, 24, 36, 48, 60], index=2)
employment_type = st.selectbox("Employment Type", ["salaried", "self-employed"])

# --- File Upload Section ---
st.subheader("Upload Salary Slip (PDF)")
uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

# --- Submit ---
if st.button("Submit Application"):

    # Input validation
    errors = []
    if not applicant_name or len(applicant_name.strip()) < 2:
        errors.append("Please enter a valid full name.")
    if stated_income <= 0:
        errors.append("Monthly income must be greater than 0.")
    if loan_amount <= 0:
        errors.append("Loan amount must be greater than 0.")
    if loan_amount > 50000000:
        errors.append("Loan amount cannot exceed Rs. 5 crore.")
    if not uploaded_file:
        errors.append("Please upload your salary slip PDF.")

    if errors:
        for error in errors:
            st.error(error)
    else:
        try:
            with st.spinner("Processing your application..."):
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

            # --- Show Results ---
            st.subheader("Application Result")

            if result["decision"] == "Approved":
                st.success(f"✅ {result['decision']}")
            elif result["decision"] == "Manual Review":
                st.warning(f"⚠️ {result['decision']} Required")
            else:
                st.error(f"❌ {result['decision']}")

            st.markdown(f"**Reason:** {result['reason']}")
            st.markdown(f"**EMI:** ₹{result['emi']:,.0f}/month")
            if result["ocr_extracted_income"]:
                st.markdown(f"**OCR Extracted Income:** ₹{result['ocr_extracted_income']:,.0f}")
            else:
                st.markdown("**OCR Extracted Income:** Could not extract — using stated income.")

            # --- Audit Trail ---
            st.subheader("Audit Trail")

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

            # --- Download Report ---
            if result.get("report_pdf"):
                st.download_button(
                    label="📄 Download Audit Report (PDF)",
                    data=result["report_pdf"],
                    file_name=f"loan_report_{result['applicant_name'].replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )

            # --- Full State ---
            with st.expander("See full application state"):
                display_state = {k: v for k, v in result.items() if k != "pdf_bytes" and k != "report_pdf"}
                st.json(display_state)

        except Exception as e:
            st.error("Something went wrong while processing the application. Please try again.")
            st.exception(e)

# --- Application History ---
st.divider()
st.subheader("Application History")
records = get_all_applications()
if records:
    history = [{
        "Name": r.applicant_name,
        "Income": f"₹{r.stated_income:,.0f}",
        "Loan": f"₹{r.loan_amount:,.0f}",
        "EMI": f"₹{r.emi:,.0f}" if r.emi else "-",
        "Risk": r.risk_tier if r.risk_tier else "-",
        "Fraud": f"{r.fraud_score:.0%}" if r.fraud_score is not None else "-",
        "Decision": r.decision,
        "Time": r.created_at.strftime("%d %b %Y, %H:%M")
    } for r in records]
    st.dataframe(history, use_container_width=True)
else:
    st.info("No applications submitted yet.")