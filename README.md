 # Blood Test Report Analyzer

A web application that extracts data from CBC (Complete Blood Count) blood test reports and displays RAG (Red/Amber/Green) status for each reading based on standard reference ranges.

## Features

- Upload CBC reports as PDF or image (PNG, JPG, JPEG, WEBP)
- Automatic extraction of patient info and test readings
- RAG status per parameter based on patient sex
- Supports multiple lab report formats
- User accounts with secure login
- Report history — view and delete past uploads

## Tech Stack

- **Backend:** Python, Flask
- **Database:** PostgreSQL
- **Libraries:** pdfplumber, pytesseract, psycopg2, bcrypt
- **Frontend:** HTML, Jinja2, Bootstrap 5

## Project Structure

```
BloodTestReportApp/
├── app.py          # Flask routes
├── extractor.py    # PDF/image text extraction and parsing
├── rag.py          # RAG status logic
├── db.py           # Database queries
├── templates/      # HTML templates
├── uploads/        # Temporary file storage (gitignored)
├── requirements.txt
├── packages.txt    # System dependencies for deployment
└── .env            # Environment variables (gitignored)
```

## Local Setup

**1. Clone the repo:**
```bash
git clone https://github.com/purple-dotcom/BloodTestReportApp
cd BloodTestReportApp
```

**2. Create and activate virtual environment:**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

**4. Install Tesseract** (for image-based reports):
- Windows: https://github.com/UB-Mannheim/tesseract/wiki
- Linux: `sudo apt-get install tesseract-ocr`

**5. Create `.env` file in project root:**
```
DB_HOST=localhost
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
SECRET_KEY=your_secret_key
```

**6. Set up the database:**

Run the following SQL to create tables:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE parameters (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    short_name VARCHAR(20),
    unit VARCHAR(30),
    ref_min_male FLOAT NOT NULL,
    ref_max_male FLOAT NOT NULL,
    ref_min_female FLOAT NOT NULL,
    ref_max_female FLOAT NOT NULL
);

CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    patient_name VARCHAR(100),
    patient_age INT,
    patient_sex VARCHAR(10),
    lab_name VARCHAR(100),
    report_date DATE,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE results (
    id SERIAL PRIMARY KEY,
    report_id INT REFERENCES reports(id) ON DELETE CASCADE,
    parameter_id INT REFERENCES parameters(id),
    value FLOAT,
    rag_status VARCHAR(10)
);
```

Then populate the parameters table:

```sql
INSERT INTO parameters (name, short_name, unit, ref_min_male, ref_max_male, ref_min_female, ref_max_female) VALUES
('Hemoglobin', 'Hb', 'g/dL', 13.0, 17.0, 12.0, 16.0),
('Total RBC Count', 'RBC', 'mill/cumm', 4.5, 5.5, 3.8, 4.8),
('Packed Cell Volume', 'PCV', '%', 40, 50, 36, 46),
('Mean Corpuscular Volume', 'MCV', 'fL', 83, 101, 83, 101),
('MCH', 'MCH', 'pg', 27, 32, 27, 32),
('MCHC', 'MCHC', 'g/dL', 32.5, 34.5, 32.5, 34.5),
('RDW', 'RDW', '%', 11.6, 14.0, 11.6, 14.0),
('Total WBC Count', 'WBC', 'cumm', 4000, 11000, 4000, 11000),
('Neutrophils', 'NEUT', '%', 50, 62, 50, 62),
('Lymphocytes', 'LYMPH', '%', 20, 40, 20, 40),
('Eosinophils', 'EOS', '%', 0, 6, 0, 6),
('Monocytes', 'MONO', '%', 0, 10, 0, 10),
('Basophils', 'BASO', '%', 0, 2, 0, 2),
('Platelet Count', 'PLT', 'cumm', 150000, 410000, 150000, 410000);
```

**7. Create uploads folder:**
```bash
mkdir uploads
```

**8. Run the app:**
```bash
python app.py
```

Visit `http://localhost:5000`

## RAG Logic

Each parameter is compared against sex-specific reference ranges:

- 🟢 **Green** — value within normal range
- 🟡 **Amber** — value within 5% buffer outside range (borderline)
- 🔴 **Red** — value significantly outside range

## Supported Report Formats

The extractor handles varying lab formats including different field labels (Sex/Gender, Age/Age+Gender combined), different date formats, and both text-based and scanned PDFs.

## Deployment

Deployed on Render. Requires the following environment variables set on the hosting platform:

```
DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, SECRET_KEY
```

System dependency for Tesseract is handled via `packages.txt`.

## Known Limitations

- Reference ranges are for adults only — paediatric ranges not supported
- Parser accuracy varies across lab formats — tested on Drlogy and Flabs report formats
- Free tier database on Render expires after 90 days
