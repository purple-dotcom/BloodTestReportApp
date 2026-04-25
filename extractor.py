import pdfplumber
import re
import pytesseract

def check_n_extract(pdf_path):
    text_found, image_found = False, False
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages[:4]:
            text = page.extract_text()
            if text and text.strip():
                text_found = True
            if page.images:
                image_found = True
    
        if text_found and image_found:
            return "mixed"
        elif image_found:
            image = pdf.pages[0].to_image().original
            return pytesseract.image_to_string(image)
        elif text_found:
            page = pdf.pages[0]
            return page.extract_text()
        else:
            return "Unknown"

loc1 = r"C:\Users\DELL\Downloads\proton-recovery-kit.pdf"
print(check_n_extract(loc1))
loc2 = r"C:\Users\DELL\Downloads\git_ref.pdf"
print(check_n_extract(loc2))