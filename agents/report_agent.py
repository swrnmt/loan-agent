from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import io

from state.loan_state import LoanState

def report_agent(state: LoanState) -> LoanState:
    """
    Generates a PDF audit report from the final state.
    Stores the PDF bytes in state["report_pdf"].
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=0.75*inch, leftMargin=0.75*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    story = []

    # --- Header ---
    header_style = ParagraphStyle('header', fontSize=18, fontName='Helvetica-Bold',
                                   alignment=1, spaceAfter=4)
    sub_style = ParagraphStyle('sub', fontSize=10, fontName='Helvetica',
                                alignment=1, spaceAfter=20, textColor=colors.grey)
    story.append(Paragraph("LOAN APPLICATION AUDIT REPORT", header_style))
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%d %B %Y, %H:%M')}", sub_style))

    # --- Decision Banner ---
    decision = state["decision"]
    if decision == "Approved":
        banner_color = colors.HexColor('#1e8449')
    elif decision == "Manual Review":
        banner_color = colors.HexColor('#d68910')
    else:
        banner_color = colors.HexColor('#922b21')

    banner_data = [[f"DECISION: {decision.upper()}"]]
    banner_table = Table(banner_data, colWidths=[6.5*inch])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), banner_color),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.white),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 14),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('PADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 0.2*inch))

    # --- Applicant Details ---
    section_style = ParagraphStyle('section', fontSize=12, fontName='Helvetica-Bold',
                                    spaceBefore=12, spaceAfter=6)
    story.append(Paragraph("Applicant Details", section_style))

    applicant_data = [
        ['Field', 'Value'],
        ['Applicant Name', state['applicant_name']],
        ['Employment Type', state['employment_type'].capitalize()],
        ['Stated Monthly Income', f"Rs. {state['stated_income']:,.0f}"],
        ['Loan Amount Requested', f"Rs. {state['loan_amount']:,.0f}"],
        ['Loan Tenure', f"{state['loan_tenure_months']} months"],
        ['Calculated EMI', f"Rs. {state['emi']:,.0f}/month"],
    ]
    applicant_table = Table(applicant_data, colWidths=[2.5*inch, 4*inch])
    applicant_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME', (0,1), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (1,1), (1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f8f9fa')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(applicant_table)

    # --- Verification Results ---
    story.append(Paragraph("Verification & Risk Assessment", section_style))

    ocr_income = f"Rs. {state['ocr_extracted_income']:,.0f}" if state['ocr_extracted_income'] else "Could not extract"
    match_status = "Match" if state['income_match'] else "Mismatch"
    mismatch = f"{state['income_mismatch_pct']:.1f}%" if state['income_mismatch_pct'] is not None else "N/A"

    verification_data = [
        ['Check', 'Result'],
        ['OCR Extracted Income', ocr_income],
        ['Income Verification', f"{match_status} ({mismatch} difference)"],
        ['Verification Confidence', f"{state['verification_confidence']:.0%}"],
        ['Debt-to-Income Ratio', f"{state['debt_to_income_ratio']:.2f}"],
        ['EMI Burden', f"{state['emi_burden_pct']:.1f}% of monthly income"],
        ['Risk Tier', state['risk_tier']],
    ]
    verification_table = Table(verification_data, colWidths=[2.5*inch, 4*inch])
    verification_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME', (0,1), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (1,1), (1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(verification_table)

    # --- Fraud Assessment ---
    story.append(Paragraph("Fraud Assessment", section_style))

    fraud_flags = state['fraud_flags'] if state['fraud_flags'] else ["No suspicious patterns detected"]
    fraud_data = [['Fraud Score', f"{state['fraud_score']:.0%}"]]
    for i, flag in enumerate(fraud_flags):
        fraud_data.append([f"Flag {i+1}" if state['fraud_flags'] else "Status", flag])

    fraud_table = Table(fraud_data, colWidths=[2.5*inch, 4*inch])
    fraud_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (1,0), (1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('PADDING', (0,0), (-1,-1), 8),
        ('TEXTCOLOR', (1,0), (1,0),
         colors.HexColor('#922b21') if state['fraud_score'] >= 0.6 else colors.HexColor('#1e8449')),
    ]))
    story.append(fraud_table)

    # --- Decision Reason ---
    story.append(Paragraph("Decision Summary", section_style))
    reason_style = ParagraphStyle('reason', fontSize=10, fontName='Helvetica',
                                   spaceAfter=6, leading=16)
    story.append(Paragraph(f"<b>Decision:</b> {state['decision']}", reason_style))
    story.append(Paragraph(f"<b>Reason:</b> {state['reason']}", reason_style))

    # --- Footer ---
    story.append(Spacer(1, 0.3*inch))
    footer_style = ParagraphStyle('footer', fontSize=8, alignment=1,
                                   textColor=colors.grey)
    story.append(Paragraph(
        "This is a system-generated audit report. "
        "All decisions are based on automated analysis and are subject to human review.",
        footer_style
    ))

    doc.build(story)
    buffer.seek(0)
    state["report_pdf"] = buffer.read()
    return state