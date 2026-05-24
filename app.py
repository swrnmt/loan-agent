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
    if not applicant_name or not uploaded_file:
        st.error("Please fill all fields and upload your salary slip.")
    else:
        with st.spinner("Processing your application..."):
            form_data = {
                "applicant_name": applicant_name,
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
            st.markdown("**OCR Extracted Income:** Could not extract")

        # --- Audit Trail ---
        st.subheader("Audit Trail")

        st.markdown(f"**Intake Agent:** Received application from {result['applicant_name']}. "
                    f"Stated income ₹{result['stated_income']:,.0f}, "
                    f"loan request ₹{result['loan_amount']:,.0f} over {result['loan_tenure_months']} months.")

        if result["ocr_extracted_income"]:
            st.markdown(f"**OCR Agent:** Extracted income of ₹{result['ocr_extracted_income']:,.0f} "
                        f"from salary slip (confidence: {result['ocr_confidence']:.0%}).")
        else:
            st.markdown("**OCR Agent:** Could not extract income from salary slip.")

        if result["income_match"]:
            st.markdown(f"**Verification Agent:** Income verified. "
                        f"Stated and extracted income match within {result['income_mismatch_pct']:.1f}%. "
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

        # --- Full State ---
        with st.expander("See full application state"):
            display_state = {k: v for k, v in result.items() if k != "pdf_bytes"}
            st.json(display_state)

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
        "Risk": r.risk_tier if hasattr(r, 'risk_tier') else "-",
        "Decision": r.decision,
        "Time": r.created_at.strftime("%d %b %Y, %H:%M")
    } for r in records]
    st.dataframe(history, use_container_width=True)
else:
    st.info("No applications submitted yet.")