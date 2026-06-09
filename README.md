# BloodTestReportApp

A Flask web application that extracts blood test parameters from PDF or image reports and displays a RAG (Red / Amber / Green) status for each reading.

Built as an internship project. Supports any standard lab report — not limited to CBC.

---

## Features

- Upload blood test reports as PDF or image (PNG, JPG, JPEG, WEBP)
- Extracts patient info: name, age, sex, lab name, report date
- Extracts test parameters and reference ranges directly from the report
- Computes RAG status with a 5% amber buffer on the reference range
- Handles multi-page PDFs — all pages processed as one report
- User authentication (signup, login, logout) with bcrypt password hashing
- Per-user report history with view and delete

---

## RAG Logic

Status is computed from the reference range printed on the report itself — no hardcoded ranges.

| Status | Condition |
|--------|-----------|
| Green  | Value within reference range |
| Amber  | Value within 5% of range width outside the boundary |
| Red    | Value beyond the amber buffer |

Buffer = `0.05 × (ref_max − ref_min)`

### Supported reference range formats

| Format | Example |
|--------|---------|
| `value unit min - max` | `82.34 mg/dl 70 - 110` |
| `value unit label : min - max` | `15.9 g/dl Adult Male : 13.5 - 17.5 g/dl` |
| `value unit Below max%` | `7.6 % Below 6.0%` (HbA1c style) — treated as range 0 to max |

> **Known limitation:** Tests with tiered categorical ranges (e.g. Average Blood Glucose with Excellent / Good / Average tiers) are evaluated against the first (strictest) numeric range found on the line. This is noted behaviour, not a bug.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python, Flask |
| Database | PostgreSQL via psycopg2 |
| PDF extraction | pdfplumber |
| OCR (scanned PDFs) | pytesseract |
| Auth | bcrypt |
| Frontend | Bootstrap 5, Jinja2 |

---

## Project Structure

```
BloodTestReportApp/
├── app.py            # Flask routes
├── extractor.py      # PDF/image text extraction and parsing
├── rag.py            # RAG status computation
├── db.py             # PostgreSQL functions
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   ├── dashboard.html
│   └── report.html
├── uploads/          # Temporary file storage (auto-deleted after processing)
├── .env              # Environment variables (not committed)
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

Connect to PostgreSQL and run the schema from the Database Schema section above.

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
2. `check_n_extract()` — if the PDF has extractable text, pdfplumber reads all pages and concatenates them; if it's a scanned image-only PDF, pytesseract OCRs the first page
3. `parse_text()` — regex patterns extract patient info and test parameters with their reference ranges
4. `get_rag_status()` — computes Green / Amber / Red for each parameter using the extracted ranges
5. Results are saved to PostgreSQL and displayed on the report page

---

## Limitations

- OCR quality depends on scan resolution; low-quality scans may miss parameters
- Categorical reference ranges (HbA1c, ABG tiers) are approximated using the first numeric range found
- Lab name extraction requires the word "Lab", "Laboratory", "Pathology", or "Diagnostics" to appear in the report header
- OCR quality depends on scan resolution; low-quality scans may produce incomplete extraction across any page
