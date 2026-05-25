import fitz
import pytesseract
from PIL import Image
import io
import os
import re
import json
import requests
from dotenv import load_dotenv

load_dotenv()

if os.name == 'nt':
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

from state.loan_state import LoanState


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract raw text from PDF. Falls back to Tesseract OCR if PDF is image-based."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    full_text = ""

    for page in doc:
        text = page.get_text()
        if text.strip():
            full_text += text
        else:
            pix = page.get_pixmap(dpi=200)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            full_text += pytesseract.image_to_string(img)

    return full_text


def extract_income_with_llm(text: str):
    """
    Use Groq LLM to intelligently extract take-home income from any salary slip format.
    Returns (income, confidence) tuple.
    """
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return None, 0.0

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {
                        "role": "system",
                        "content": """You are a salary slip parser. Your only job is to find the final monthly take-home amount — the money actually deposited into the employee's bank account after all deductions.

PRIORITY ORDER — search for these labels in this exact order and return the FIRST match:
1. Take Home Pay
2. Net Salary
3. Net Pay
4. Net Amount
5. In Hand Salary
6. Total Net
7. Net Wages
8. Amount Payable
9. Final Pay
10. Net Disbursement
11. Total Take Home

IMPORTANT RULES:
- NEVER return Basic Salary, Gross Salary, Gross Earnings, or CTC — these are NOT take-home
- The take-home is always LESS than gross earnings because deductions are subtracted
- If you see a green or highlighted row at the bottom of the slip, that is usually the take-home
- Numbers can appear as 1,22,800 or 122800 or Rs. 1,22,800 or INR 1,22,800 — treat them all the same
- Return ONLY this exact JSON format with no other text:
{"income": 122800.0, "confidence": 0.9}
- confidence should be 0.95 if label clearly matches, 0.8 if you inferred it, 0.0 if not found
- If you genuinely cannot find the take-home: {"income": null, "confidence": 0.0}"""
                    },
                    {
                        "role": "user",
                        "content": f"Extract the monthly take-home pay from this salary slip text. Remember — NOT gross salary, NOT basic salary. The final amount after all deductions:\n\n{text[:4000]}"
                    }
                ],
                "max_tokens": 80,
                "temperature": 0
            },
            timeout=15
        )

        content = response.json()["choices"][0]["message"]["content"].strip()
        content = content.replace("```json", "").replace("```", "").strip()
        data = json.loads(content)

        income = data.get("income")
        confidence = float(data.get("confidence", 0.0))

        if income and confidence > 0.5:
            # Sanity check: must be a realistic monthly income
            if 3000 <= float(income) <= 10000000:
                return float(income), confidence

        return None, 0.0

    except Exception as e:
        print(f"LLM extraction error: {e}")
        return None, 0.0


def extract_income_with_regex(text: str):
    """
    Fallback regex extraction if LLM fails.
    Covers common Indian salary slip formats.
    """
    patterns = [
        # Explicit take-home labels
        r"(?:take\s*home\s*pay|net\s*salary|net\s*pay|in\s*hand|net\s*amount|amount\s*payable)[^\d]{0,30}(?:INR|Rs\.?|₹)?\s*([\d,]+)",
        # INR prefix patterns
        r"(?:net\s*pay|monthly\s*income)[^\d]{0,20}INR\s*([\d,]+)",
        # End of line INR patterns
        r"INR\s*([\d,]+)(?=\s*$)",
        # Generic fallback
        r"(?:net\s*pay|monthly\s*income|salary)[^\d]{0,10}([\d]{2,3}[,\d]+)",
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            value = match.replace(",", "")
            try:
                candidate = float(value)
                if 3000 <= candidate <= 10000000:
                    return candidate
            except:
                continue

    return None


def ocr_agent(state: LoanState) -> LoanState:
    """
    Extracts monthly take-home income from salary slip PDF.
    Strategy:
    1. Extract raw text using PyMuPDF (free)
    2. Send to Groq LLM for intelligent extraction (handles any format)
    3. Fall back to regex if LLM fails
    4. Fall back to stated income if both fail
    """
    pdf_bytes = state["pdf_bytes"]

    # Step 1: Extract raw text
    full_text = extract_text_from_pdf(pdf_bytes)

    # Step 2: LLM-based extraction
    extracted_income, confidence = extract_income_with_llm(full_text)

    # Step 3: Regex fallback
    if extracted_income is None:
        print("LLM extraction failed, trying regex fallback...")
        extracted_income = extract_income_with_regex(full_text)
        confidence = 0.7 if extracted_income else 0.0

    # Step 4: Log result
    if extracted_income:
        print(f"OCR extracted: ₹{extracted_income:,.0f} (confidence: {confidence:.0%})")
    else:
        print("OCR failed — will fall back to stated income in decision agent")

    state["ocr_extracted_income"] = extracted_income
    state["ocr_confidence"] = confidence

    return state