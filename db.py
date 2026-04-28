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
    for short_name, data in rag_status.items():
        para_id = get_parameter_id(short_name)
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

#TESTING
# if __name__ == '__main__':
#     user_id = create_user("Test", "test69@gmail.com", "password123")
#     print(f"Created User : {user_id}")

#     user = get_user_by_email("test69@gmail.com")
#     print("Fetched user:", user)

#     user = get_user_by_id(user_id)
#     print("Fetched by id:", user)

#     report_id = create_report(user_id, "Test", 25, "Male", "Test Lab", "2011-11-11")
#     print(f"Created report : {report_id}")

#     reports = get_reports_by_user(user_id)
#     print(f"Reports fetched : {reports}")

#     param_id = get_parameter_id("Hb")
#     print("Parameter id:", param_id)

#     dummy = {
#         "Hb": {"value": 12.5, "status": "Red"},
#         "RBC": {"value": 5.2, "status": "Green"}
#     }
#     save_results(report_id, dummy)
#     print("Results saved")

#     results = get_results_by_report(report_id)
#     print("Results:", results)

#     delete_report(report_id)
#     print("Report deleted")