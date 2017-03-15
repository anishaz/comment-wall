from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX = re.compile(r'[a-zA-Z]')

app = Flask(__name__)

app.secret_key = "thisisasupersecretkey"

mysql = MySQLConnector(app,'walldb')

def checkUserLogin():
    session['logged-in'] = True
    global loggedIn
    loggedIn = session['logged-in']
    if loggedIn == True:
        print 'cookie is true'
    else:
        print 'cookie is false'


@app.route('/')
def index():
    return render_template('welcome.html')

@app.route('/register', methods=["POST"])
def register():
    valid = True

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

    data = {
        'first_name': request.form['firstName'],
        'last_name': request.form['lastName'],
        'email': request.form['email'],
        'password': request.form['password']
    }

    query = "INSERT INTO users (first_name, last_name, email, password) VALUES (:first_name, :last_name, :email, :password)"
    mysql.query_db(query,data)
    print "registered"
    checkUserLogin()
    return redirect('/wall')

@app.route('/login', methods=["POST"])
def login ():
    print "logged in"

    data = {
        'email': request.form['email']
    }

    user_email = mysql.query_db("SELECT id, email, password FROM users WHERE email = :email", data)
    if user_email:
        if request.form['password'] == user_email[0]['password']:
            session['user'] = user_email[0]['id']
            flash("Welcome Back!")
        else:
            flash("Incorrect password. Please try again")
            return redirect('/')
    else:
        flash("Invalid e-mail address. Please try again or register if it is your first time here.")
        return redirect('/')

    return render_template("wall.html")

@app.route('/wall', methods=["GET", "POST"])
def something():
    print "yea!"
    #shows a list of the current list of messages
    query = "SELECT * FROM messages"
    messages = mysql.query_db(query)

    #function for adding the messages to the list
    # query = "INSERT INTO messages (message) VALUES (:message)"
    #
    # data = {
    #          'message': request.form['message']
    # }
    #
    # mysql.query_db(query,data)
    return render_template('wall.html', all_messages = messages)

app.run(debug=True)
