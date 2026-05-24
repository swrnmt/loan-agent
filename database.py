from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import sqlite3

Base = declarative_base()
engine = create_engine("sqlite:///loan_applications.db")
Session = sessionmaker(bind=engine)

class LoanApplication(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True)
    applicant_name = Column(String)
    stated_income = Column(Float)
    loan_amount = Column(Float)
    loan_tenure_months = Column(Integer)
    employment_type = Column(String)
    ocr_extracted_income = Column(Float)
    ocr_confidence = Column(Float)
    income_match = Column(String)
    income_mismatch_pct = Column(Float)
    verification_confidence = Column(Float)
    debt_to_income_ratio = Column(Float)
    emi_burden_pct = Column(Float)
    risk_tier = Column(String)
    fraud_score = Column(Float)
    emi = Column(Float)
    decision = Column(String)
    reason = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

def migrate_db():
    conn = sqlite3.connect("loan_applications.db")
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(applications)")
    existing_columns = [row[1] for row in cursor.fetchall()]

    new_columns = {
        "income_match": "TEXT",
        "income_mismatch_pct": "REAL",
        "verification_confidence": "REAL",
        "debt_to_income_ratio": "REAL",
        "emi_burden_pct": "REAL",
        "risk_tier": "TEXT",
        "fraud_score": "REAL",
    }

    for column, col_type in new_columns.items():
        if column not in existing_columns:
            cursor.execute(f"ALTER TABLE applications ADD COLUMN {column} {col_type}")

    conn.commit()
    conn.close()

def init_db():
    Base.metadata.create_all(engine)
    migrate_db()

def save_application(state: dict):
    session = Session()
    record = LoanApplication(
        applicant_name=state.get("applicant_name"),
        stated_income=state.get("stated_income"),
        loan_amount=state.get("loan_amount"),
        loan_tenure_months=state.get("loan_tenure_months"),
        employment_type=state.get("employment_type"),
        ocr_extracted_income=state.get("ocr_extracted_income"),
        ocr_confidence=state.get("ocr_confidence"),
        income_match=str(state.get("income_match")),
        income_mismatch_pct=state.get("income_mismatch_pct"),
        verification_confidence=state.get("verification_confidence"),
        debt_to_income_ratio=state.get("debt_to_income_ratio"),
        emi_burden_pct=state.get("emi_burden_pct"),
        risk_tier=state.get("risk_tier"),
        fraud_score=state.get("fraud_score"),
        emi=state.get("emi"),
        decision=state.get("decision"),
        reason=state.get("reason"),
    )
    session.add(record)
    session.commit()
    session.close()

def get_all_applications():
    session = Session()
    records = session.query(LoanApplication).order_by(
        LoanApplication.created_at.desc()
    ).all()
    session.close()
    return records