import streamlit as st
from main import run_pipeline

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

        # --- Show Results ---
        st.subheader("Application Result")

        if result["decision"] == "Approved":
            st.success(f"✅ {result['decision']}")
        else:
            st.error(f"❌ {result['decision']}")

        st.markdown(f"**Reason:** {result['reason']}")
        st.markdown(f"**EMI:** ₹{result['emi']:,.0f}/month")
        st.markdown(f"**OCR Extracted Income:** ₹{result['ocr_extracted_income']:,.0f}" if result['ocr_extracted_income'] else "**OCR Extracted Income:** Could not extract")

        # --- Full State (for debugging) ---
        with st.expander("See full application state"):
            st.json(result)