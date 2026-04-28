import psycopg2 as psy

def get_connection():
    return psy.connect(
        host = "localhost",
        database = "bloodtestreport",
        user = "postgres", 
        password = "P@ssw0rd"
        )
# cursor = con.cursor()

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

#--REPORT--#
def create_report(user_id, name, age, sex, lab_name, report_date):
    con = get_connection()
    cursor = con.cursor()
    cursor.execute("INSERT INTO reports (patient_name, patient_age, patient_sex, lab_name, report_date) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id", (user_id, name, age, sex, lab_name, report_date))
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

def delete_report(report_id):
    con = get_connection()
    cursor = con.cursor()
    cursor.execute("DELETE FROM reports where report_id = %s", (report_id,))
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
    cursor.execute("")