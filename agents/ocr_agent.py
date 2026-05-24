import fitz
import pytesseract
from PIL import Image
import io
import re

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

from state.loan_state import LoanState

def ocr_agent(state: LoanState, pdf_bytes: bytes) -> LoanState:
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

    # Uncomment this line temporarily to see what text is being extracted:
    # print("EXTRACTED TEXT:\n", full_text)

    patterns = [
        r"(?:net\s*pay|monthly\s*income)[^\d]{0,20}INR\s*([\d,]+)",
        r"(?:net\s*pay|monthly\s*income)\s*/[^\d]{0,20}INR\s*([\d,]+)",
        r"INR\s*([\d,]+)(?=\s*$)",
        r"(?:net\s*pay|monthly\s*income|salary)[^\d]{0,10}([\d]{2,3}[,\d]+)",
    ]

    extracted = None
    for pattern in patterns:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match:
            value = match.group(1).replace(",", "")
            candidate = float(value)
            # Sanity check: monthly income should be between 5,000 and 10,000,000
            if 5000 <= candidate <= 10000000:
                extracted = candidate
                break

    state["ocr_extracted_income"] = extracted
    state["ocr_confidence"] = 0.9 if extracted else 0.0

    return state