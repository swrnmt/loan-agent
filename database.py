from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

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
    emi = Column(Float)
    decision = Column(String)
    reason = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(engine)

def save_application(state: dict):
    session = Session()
    record = LoanApplication(
        applicant_name=state["applicant_name"],
        stated_income=state["stated_income"],
        loan_amount=state["loan_amount"],
        loan_tenure_months=state["loan_tenure_months"],
        employment_type=state["employment_type"],
        ocr_extracted_income=state.get("ocr_extracted_income"),
        ocr_confidence=state.get("ocr_confidence"),
        emi=state.get("emi"),
        decision=state.get("decision"),
        reason=state.get("reason"),
    )
    session.add(record)
    session.commit()
    session.close()

def get_all_applications():
    session = Session()
    records = session.query(LoanApplication).order_by(LoanApplication.created_at.desc()).all()
    session.close()
    return records