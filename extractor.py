import pdfplumber
import re
import pytesseract

def check_pdf_type(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        global text_found
        global image_found 
        text_found, image_found = False, False

        for page in pdf.pages[:4]:
            if page.extract_text():
                text_found = True
            if page.images:
                image_found = True

        if text_found and not image_found:
            return "text"
        if image_found and not text_found:
            return "image"
        elif image_found and text_found:
            return "mixed"
        else:
            return "Unknown"
        
def extraction():
    global txt
    if pdf_type == 'text':
        with pdfplumber.open(loc) as pdf:
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
pdf_type = check_pdf_type(loc)
extraction()
