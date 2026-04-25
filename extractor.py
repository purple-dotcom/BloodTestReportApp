import pdfplumber
import re
import pytesseract

def check_pdf_type(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text_found, image_found = False, False

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
        txt = page.extract_text()
        return txt
    else:
        return "Unknown"
        
def extraction(pdf_path, pdf_type):
    if pdf_type == 'text':
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[0]
            txt = page.extract_text()
        print(txt)

    elif pdf_type == "image":
        pass
    elif pdf_type == "mixed":
        pass
    else:
        pass

loc = r"C:\Users\DELL\Downloads\proton-recovery-kit.pdf"
# pdf_type = check_pdf_type(loc)
extraction(loc, check_pdf_type(loc))