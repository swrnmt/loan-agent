from typing import TypedDict, Optional

class LoanState(TypedDict):
    # Intake Agent fills these
    applicant_name: str
    stated_income: float
    loan_amount: float
    loan_tenure_months: int
    employment_type: str

    # OCR Agent fills these
    ocr_extracted_income: Optional[float]
    ocr_confidence: Optional[float]

    # Decision Agent fills these
    emi: Optional[float]
    decision: Optional[str]
    reason: Optional[str]