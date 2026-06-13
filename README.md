# BloodTestReportApp

A Flask web application that extracts blood test parameters from PDF or image reports and displays a RAG (Red / Amber / Green) status for each reading, evaluated against clinically validated reference ranges adjusted for the patient's age and sex.

Built as an internship project. Supports any standard lab report — not limited to CBC.

---

## Features

- Upload blood test reports as PDF or image (PNG, JPG, JPEG, WEBP)
- Extracts patient info: name, age, sex, lab name, report date
- Extracts parameter names and values from the report
- Normalises parameter names across lab formats to a canonical name (e.g. `HAEMOGLOBIN`, `Hb`, `HGB` → `Hemoglobin`)
- Evaluates readings against hardcoded clinical reference ranges with explicit amber zones, adjusted for patient age and sex
- Handles multi-page PDFs — all pages processed as one report
- User authentication (signup, login, logout) with bcrypt password hashing
- Per-user report history with view and delete

---

## RAG Logic

Status is computed by looking up the parameter in a `parameters` table keyed by canonical name, sex, and age bracket. Each row stores an explicit Green zone and Amber zone — no blanket percentage buffer.

| Status | Condition |
|--------|-----------|
| Green  | `ref_min ≤ value ≤ ref_max` |
| Amber  | `amber_low ≤ value < ref_min` or `ref_max < value ≤ amber_high` |
| Red    | `value < amber_low` or `value > amber_high` |

The lookup prefers an exact sex match over `Any`, and a narrower age range over a wider one, so the most specific applicable row always wins.

---

## Supported Parameters

| Category | Parameters |
|----------|------------|
| CBC | Hemoglobin, WBC, Neutrophils, Lymphocytes, Monocytes, Eosinophils, Basophils, Platelets, RBC, HCT, MCV, MCH, MCHC, PDW, MPV, RDW-CV |
| Glucose | Glucose Fasting, Glucose Random, Glucose PP |
| Diabetes | HbA1c, Average Blood Glucose |
| Liver Function | Total Bilirubin, Conjugated Bilirubin, Unconjugated Bilirubin, Total Protein, Albumin |

Parameters not in this list are silently skipped — no RAG status is shown for them.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python, Flask |
| Database | PostgreSQL via psycopg2 |
| PDF extraction | pdfplumber |
| OCR (scanned PDFs / images) | pytesseract |
| Auth | bcrypt |
| Frontend | Bootstrap 5, Jinja2 |

---

## Project Structure

```
BloodTestReportApp/
├── app.py                  # Flask routes
├── extractor.py            # PDF/image extraction, parsing, name normalisation
├── rag.py                  # RAG status computation
├── db.py                   # PostgreSQL functions
├── parameters_seed.sql     # Reference range data for the parameters table
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   ├── dashboard.html
│   └── report.html
├── uploads/                # Temporary file storage (auto-deleted after processing)
├── .env                    # Environment variables (not committed)
└── requirements.txt
```

---

## Database Schema

```sql
CREATE TABLE users (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(100),
    email         VARCHAR(100) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    is_active     BOOLEAN DEFAULT TRUE,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reports (
    id            SERIAL PRIMARY KEY,
    user_id       INT REFERENCES users(id),
    patient_name  VARCHAR(100),
    patient_age   INT,
    patient_sex   VARCHAR(10),
    lab_name      VARCHAR(100),
    report_date   DATE,
    uploaded_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE results (
    id             SERIAL PRIMARY KEY,
    report_id      INT REFERENCES reports(id) ON DELETE CASCADE,
    parameter_name VARCHAR(150),
    value          FLOAT,
    ref_min        FLOAT,
    ref_max        FLOAT,
    rag_status     VARCHAR(10)
);

CREATE TABLE parameters (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(150),
    sex        VARCHAR(10),    -- 'Male', 'Female', or 'Any'
    age_min    INT DEFAULT 0,
    age_max    INT DEFAULT 999,
    ref_min    FLOAT,
    ref_max    FLOAT,
    amber_low  FLOAT,
    amber_high FLOAT
);
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/purple-dotcom/BloodTestReportApp
cd BloodTestReportApp
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```
SECRET_KEY=your_secret_key_here
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
```

### 5. Set up the database

Connect to PostgreSQL, run the schema above, then seed the parameters table:

```bash
psql -U your_db_user -d your_db_name -f parameters_seed.sql
```

### 6. Install Tesseract (for scanned PDF / image support)

Download and install from https://github.com/UB-Mannheim/tesseract/wiki and ensure the binary is on your PATH.

### 7. Run the app

```bash
python app.py
```

Visit `http://127.0.0.1:5000`

---

## How It Works

1. User uploads a PDF or image
2. `check_n_extract()` — pdfplumber reads all pages of text-based PDFs; pytesseract OCRs all pages of scanned PDFs or direct image uploads
3. `parse_text()` — regex patterns extract patient demographics and parameter name + value pairs from the raw text
4. `normalize_readings()` — maps raw PDF names to canonical names so they match the parameters table (e.g. `TOTAL LEUKOCYTE COUNT` → `WBC`)
5. `get_rag_status()` — looks up each canonical name in the parameters table using the patient's age and sex, then computes Green / Amber / Red against the stored boundaries
6. Results are saved to PostgreSQL and displayed on the report page

---

## Limitations

- Only parameters listed in the `parameters` table receive a RAG status; anything else is skipped
- Platelets are stored in lakhs/cumm (standard in Indian labs); reports using 10³/μL will produce incorrect results
- OCR quality depends on scan resolution — low-quality scans may misread values or miss parameters entirely
- Lab name extraction requires the word "Lab", "Laboratory", "Pathology", or "Diagnostics" to appear in the report header
- If age or sex cannot be extracted from the report, age defaults to 0 and sex defaults to Male for the range lookup