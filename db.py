import psycopg2 as psy
from dotenv import load_dotenv
import os

load_dotenv()

def get_connection():
    return psy.connect(
        host = os.getenv("DB_HOST"),
        port = os.getenv("DB_PORT", 5432),
        database = os.getenv("DB_NAME"),
        user = os.getenv("DB_USER"), 
        password = os.getenv("DB_PASSWORD")
        )

#--USER--#
def create_user(name, email, password):
    con = get_connection()
    cursor = con.cursor()
    cursor.execute("INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s) RETURNING id", 
                   (name, email, password))
    user_id = cursor.fetchone()[0]
    con.commit()
    cursor.close()
    con.close()
    return user_id

def get_user_by_email(email):
    con = get_connection()
    cursor = con.cursor()
    cursor.execute("SELECT id, name, email, password_hash FROM users WHERE email = %s", (email,))
    result = cursor.fetchone()
    cursor.close()
    con.close()
    return result

def get_user_by_id(user_id):
    con = get_connection()
    cursor = con.cursor()
    cursor.execute('SELECT id, name, email FROM users WHERE id = %s', (user_id,))
    result = cursor.fetchone()
    cursor.close()
    con.close()
    return result

#--REPORT--#
def create_report(user_id, name, age, sex, lab_name, report_date):
    con = get_connection()
    cursor = con.cursor()
    cursor.execute("INSERT INTO reports (user_id, patient_name, patient_age, patient_sex, lab_name, report_date) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id", (user_id, name, age, sex, lab_name, report_date))
    report_id = cursor.fetchone()[0]
    con.commit()
    cursor.close()
    con.close()
    return report_id

def get_reports_by_user(user_id):
    con = get_connection()
    cursor = con.cursor()
    cursor.execute("SELECT id, patient_name, report_date, uploaded_at FROM reports WHERE user_id = %s ORDER BY uploaded_at DESC", (user_id,))
    result = cursor.fetchall()
    cursor.close()
    con.close()
    return result

def get_report_by_id(report_id):
    con = get_connection()
    cursor = con.cursor()
    cursor.execute("SELECT id, user_id, patient_name, lab_name, report_date FROM reports WHERE id = %s", (report_id,))
    result = cursor.fetchone()
    cursor.close()
    con.close()
    return result

def delete_report(report_id):
    con = get_connection()
    cursor = con.cursor()
    cursor.execute("DELETE FROM reports where id = %s", (report_id,))
    con.commit()
    cursor.close()
    con.close()

#--RESULT--#
def get_parameter_id(short_name):
    con = get_connection()
    cursor = con.cursor()
    cursor.execute("SELECT id FROM parameters WHERE short_name = %s", (short_name,))
    result = cursor.fetchone()
    cursor.close()
    con.close()
    return result[0] if result else None

def save_results(report_id, rag_status):
    con = get_connection()
    cursor = con.cursor()
    cursor.execute("SELECT short_name, id FROM parameters")
    param_map = {row[0]: row[1] for row in cursor.fetchall()}
    
    for short_name, data in rag_status.items():
        para_id = param_map.get(short_name)
        if para_id is None:
            continue
        cursor.execute("INSERT INTO results (report_id, parameter_id, value, rag_status) VALUES (%s, %s, %s, %s)", (report_id, para_id, data['value'], data['status']))
    
    con.commit()
    cursor.close()
    con.close()

def get_results_by_report(report_id):
    con = get_connection()
    cursor = con.cursor()
    cursor.execute(
        '''SELECT p.name, p.short_name, p.unit, r.value, r.rag_status
        FROM results r
        JOIN parameters p 
        ON r.parameter_id = p.id
        WHERE r.report_id = %s''',
        (report_id,))
    result = cursor.fetchall()
    cursor.close()
    con.close()
    return result