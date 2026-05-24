from typing import TypedDict, Optional, List

class LoanState(TypedDict):
    # Intake Agent fills these
    applicant_name: str
    stated_income: float
    loan_amount: float
    loan_tenure_months: int
    employment_type: str
    pdf_bytes: Optional[bytes]

    # OCR Agent fills these
    ocr_extracted_income: Optional[float]
    ocr_confidence: Optional[float]

    # Verification Agent fills these
    income_match: Optional[bool]
    income_mismatch_pct: Optional[float]
    verification_flags: Optional[List[str]]
    verification_confidence: Optional[float]

    # Risk Agent fills these
    debt_to_income_ratio: Optional[float]
    emi_burden_pct: Optional[float]
    risk_tier: Optional[str]  # "Low", "Medium", "High"

    # Fraud Agent fills these
    fraud_flags: Optional[List[str]]
    fraud_score: Optional[float]  # 0 to 1

    # Decision Agent fills these
    emi: Optional[float]
    decision: Optional[str]  # "Approved", "Rejected", "Manual Review"
    reason: Optional[str]

    report_pdf: Optional[bytes]