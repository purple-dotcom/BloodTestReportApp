import pdfplumber
import pytesseract
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os

def check_n_extract(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text_pages = []
        for page in pdf.pages:
            text = page.extract_text()
            if text and text.strip():
                text_pages.append(text)

        if text_pages:
            return '\n'.join(text_pages)

        scanned_pages = []
        for page in pdf.pages:
            scanned_pages.append(pytesseract.image_to_string(page.to_image().original))
        
        return '\n'.join(scanned_pages)
    
# loc = r"C:\Users\ayaan\Downloads\git-cheatsheet.pdf"
# print(check_n_extract(loc))

def add(x,y):
    pp = x + y
    ll = x - y
    return pp, ll

x, y = add(5,6)
print(x)
print(y)

filepath = r"C:\Users\ayaan\Downloads\IRFAN SHAIKH_1777724991000.pdf"
x = secure_filename(filename = filepath)
print(x)

r = {'x':66, 'y':99, 'z':100}
for i in r.items():
    print(i)

print(os.getenv("JAVA_HOME"))
load_dotenv(override=True)
print(os.getenv("JAVA_HOME"))
print(os.getenv("DB_HOST"))

class File():
    def __init__(self, filename):
        self.filename = filename

uploaded_file = File("../../../windows/system32/important.dll")

safe_name = secure_filename(uploaded_file.filename)
print(safe_name)