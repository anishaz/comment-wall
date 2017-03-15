from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX = re.compile(r'[a-zA-Z]')

app = Flask(__name__)

app.secret_key = "thisisasupersecretkey"

mysql = MySQLConnector(app,'walldb')

@app.route('/')
def index():
    return render_template('welcome.html')

@app.route('/register', methods=['POST'])
def register():
    valid = True
    flash("Thank you for registering!")

    # check if all fields are being entered since nothing can be blank
    for field in request.form:
        if len(request.form[field]) == 0:
            flash(field + " must not be blank. Please check and re-submit.")
            valid = False

    # check for email validation
    if len(request.form['email']) > 1 and not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid Email Address. Please try again.")
        valid = False

    # First name must be valid
    if len(request.form['firstName']) > 1 and not NAME_REGEX.match(request.form['firstName']):
        flash("Invalid First Name. Please try again.")
        valid = False

    # Last name must be valid
    if len(request.form['lastName']) > 1 and not NAME_REGEX.match(request.form['lastName']):
        flash("Invalid Last Name. Please try again.")
        valid = False

    # Password must match confirm password
    if not request.form['password'] == request.form['confirmPassword']:
        flash("Password and confirm password must match. Please try again.")
        valid = False

    if(valid == False):
        return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    session['logged-in'] = True
    loggedIn = session['logged-in']
    if loggedIn == False:
        print 'cookie is true'
    return redirect('/welcome')

@app.route('/wall', methods=['POST'])
def checkLoginStatus():
    if loggedIn == False:
        return redirect('/login')

    #shows a list of the current list of emails
    # query = "SELECT * FROM emails"
    # emails = mysql.query_db(query)
    #
    # # function for adding the emails to the list
    # query = "INSERT INTO emails (email, created_at) VALUES (:email, NOW())"
    #
    # data = {
    #         'email': request.form['email']
    # }
    #
    # mysql.query_db(query,data)
    return render_template('wall.html')

app.run(debug=True)
