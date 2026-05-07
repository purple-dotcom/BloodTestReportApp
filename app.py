from flask import Flask, render_template, url_for, request, redirect, session
import bcrypt
from extractor import *
from rag import get_rag_status
from db import *

app = Flask(__name__)
app.secret_key = "chain kulli ki main kulli"

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
            password_hash = bcrypt.hashpw(request.form["password"].encode("utf-8"), bcrypt.gensalt())

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

        if bcrypt.checkpw(request.form["password"].encode("utf-8"), bytes(user[3])):
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
    pass

@app.route("delete/<int:report_id>", methods = ["POST"])
def delete():
    pass

@app.route("/logout")
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)