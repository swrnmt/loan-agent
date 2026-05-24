from main import run_pipeline

# 10 simulated profiles
# Format: (name, stated_income, loan_amount, tenure, employment_type, salary_slip)
# We'll use dummy_salary_slip.pdf (income: 71250) for all tests

with open("dummy_salary_slip.pdf", "rb") as f:
    pdf_bytes = f.read()

profiles = [
    # 3 should Approve
    {"applicant_name": "Priya Mehta",     "stated_income": 80000,  "loan_amount": 500000,  "loan_tenure_months": 36, "employment_type": "salaried"},
    {"applicant_name": "Arjun Kapoor",    "stated_income": 75000,  "loan_amount": 400000,  "loan_tenure_months": 24, "employment_type": "salaried"},
    {"applicant_name": "Sneha Iyer",      "stated_income": 70000,  "loan_amount": 600000,  "loan_tenure_months": 48, "employment_type": "salaried"},

    # 3 should Reject
    {"applicant_name": "Karan Malhotra",  "stated_income": 50000,  "loan_amount": 2000000, "loan_tenure_months": 36, "employment_type": "salaried"},
    {"applicant_name": "Divya Nair",      "stated_income": 40000,  "loan_amount": 1500000, "loan_tenure_months": 24, "employment_type": "salaried"},
    {"applicant_name": "Rohit Self",      "stated_income": 90000,  "loan_amount": 800000,  "loan_tenure_months": 36, "employment_type": "self-employed"},

    # 2 should Manual Review (fraud flags)
    {"applicant_name": "Amit Dubey",      "stated_income": 200000, "loan_amount": 800000,  "loan_tenure_months": 36, "employment_type": "salaried"},
    {"applicant_name": "Neha Fake",       "stated_income": 150000, "loan_amount": 600000,  "loan_tenure_months": 36, "employment_type": "salaried"},

    # 2 edge cases
    {"applicant_name": "Raj Borderline",  "stated_income": 71250,  "loan_amount": 700000,  "loan_tenure_months": 36, "employment_type": "salaried"},
    {"applicant_name": "Meera Exact",     "stated_income": 71250,  "loan_amount": 500000,  "loan_tenure_months": 36, "employment_type": "salaried"},
]

print(f"\n{'='*70}")
print(f"{'NAME':<20} {'INCOME':>10} {'LOAN':>12} {'RISK':<10} {'FRAUD':>7} {'DECISION'}")
print(f"{'='*70}")

for profile in profiles:
    result = run_pipeline(profile, pdf_bytes)
    print(f"{result['applicant_name']:<20} "
          f"₹{result['stated_income']:>9,.0f} "
          f"₹{result['loan_amount']:>11,.0f} "
          f"{result['risk_tier']:<10} "
          f"{result['fraud_score']:>6.0%} "
          f"{result['decision']}")

print(f"{'='*70}\n")