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
    
        if text_found:  #ignore decorative images
            return pdf.pages[0].extract_text()
        elif image_found:  # no text at all, actual scanned pdf
            image = pdf.pages[0].to_image().original
            return pytesseract.image_to_string(image)
        else:
            return "unknown"

# loc1 = r"C:\Users\DELL\Downloads\proton-recovery-kit.pdf"
# print(check_n_extract(loc1))
loc2 = r"C:\Users\DELL\Downloads\CBC-test-report-format-example-sample-template-Drlogy-lab-report.pdf"
txt = check_n_extract(loc2)
print(txt)