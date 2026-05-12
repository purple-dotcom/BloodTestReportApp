from flask import Flask, render_template, url_for, request, redirect, session
import bcrypt
from extractor import check_n_extract, parse_text, get_short_name_values
from rag import get_rag_status
from db import *
import os
from dotenv import load_dotenv
from datetime import timedelta


app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.permanent_session_lifetime = timedelta(days=7)

@app.context_processor
def inject_session():
    return dict(session=session)

@app.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route("/signup", methods = ["GET", "POST"])
def signup():
    if request.method == "POST":
            namex = request.form['name']
            emailx = request.form['email']
            password_hash = bcrypt.hashpw(request.form["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

            if get_user_by_email(emailx):
                return render_template('signup.html', error = "Email already registered")
            
            session["user_id"] = create_user(namex, emailx, password_hash)
            return redirect(url_for('dashboard'))
    
    return render_template('signup.html')

@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        emailx = request.form['email']
        user = get_user_by_email(emailx)

        if not user:
            return render_template('login.html', error = "Email not found")

        if bcrypt.checkpw(request.form["password"].encode("utf-8"), user[3].encode("utf-8")):
            session.permanent = True
            session['user_id'] = user[0]
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error = "Wrong password")
        
    return render_template('login.html')


@app.route("/dashboard")
def dashboard():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    reports = get_reports_by_user(session['user_id'])
    return render_template('dashboard.html', reports = reports)

@app.route("/upload", methods = ["POST"])
def upload():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    file = request.files['pdf']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    
    text = check_n_extract(filepath)
    os.remove(filepath)
    patient_info, raw_readings = parse_text(text)
    clean_readings = get_short_name_values(raw_readings)
    rag_results = get_rag_status(clean_readings, patient_info['sex'])

    report_id = create_report(
        session['user_id'],
        patient_info.get('name', 'Unknown'),
        patient_info.get('age'),
        patient_info.get('sex'),
        patient_info.get('lab_name', 'Unknown Lab'),
        patient_info.get('report_date')
    )

    save_results(report_id, rag_results)
    return redirect(url_for('view_report', report_id = report_id))

@app.route("/report/<int:report_id>")
def view_report(report_id):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    report = get_report_by_id(report_id)
    if not report or report[1] != session['user_id']:
        return "Unauthorized", 403
    
    results = get_results_by_report(report_id)
    return render_template('report.html', results = results, report = report)


@app.route("/delete/<int:report_id>", methods = ["POST"])
def delete(report_id):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    report = get_report_by_id(report_id)
    if not report or report[1] != session['user_id']:
        return "Unauthorized", 403
    
    delete_report(report_id)
    return redirect(url_for('dashboard'))


@app.route("/logout")
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)