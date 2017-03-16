from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import bcrypt, re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX = re.compile(r'[a-zA-Z]')

app = Flask(__name__)

app.secret_key = "thisisasupersecretkey"

mysql = MySQLConnector(app,'walldb')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=["POST"])
def register():
    valid = True
    flash("You have successfully registered. Please login below.")

    # check if all fields are being entered since nothing can be blank
    for field in request.form:
        if len(request.form[field]) == 0:
            flash(field.replace("_", " ") + " must not be blank. Please check and re-submit.")
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

    return redirect('/')

@app.route('/login', methods=["POST"])
def login():
    data = {
        'email': request.form['email']
    }

    user_email = mysql.query_db("SELECT id, email, password, first_name FROM users WHERE email = :email", data)
    if user_email:
        if request.form['password'] == user_email[0]['password']:
            session['user'] = user_email[0]['id']
            session['name'] = user_email[0]['first_name']
            return redirect('/wall')
        else:
            flash("Incorrect password. Please try again")
            return redirect('/')
    else:
        flash("Invalid e-mail address. Please try again or register if it is your first time here.")
        return redirect('/')

@app.route('/wall')
def wall():

    msg_query = "SELECT CONCAT(users.first_name, ' ', users.last_name) AS name, messages.* FROM messages JOIN users ON users.id = messages.user_id ORDER BY created_at DESC;"

    comment_query = "SELECT * FROM comments;"
    messages = mysql.query_db(msg_query)
    for message in messages:
        data = {
            'message_id': message['id']
        }
        message['comments'] = mysql.query_db("SELECT comments.*, CONCAT(users.first_name, ' ', users.last_name) AS name FROM  comments JOIN users ON users.id = comments.user_id WHERE message_id = :message_id", data)

    comments = mysql.query_db(comment_query)

    return render_template("wall.html", messages = messages, comments = comments)

@app.route('/message', methods=["POST"])
def message():

    data = {
        'user_id': session['user'],
        'message': request.form['message']
    }

    message_insert_query = "INSERT INTO messages (user_id, message) VALUES (:user_id, :message)"
    message_id = mysql.query_db(message_insert_query, data)

    return redirect ('/wall')

@app.route('/comment/<message_id>', methods=["POST"])
def comment(message_id):

    data = {
        'user_id': session['user'],
        'post_id': message_id,
        'comment': request.form['comment']
    }

    comment_insert_query = "INSERT INTO comments (user_id, message_id, comment) VALUES (:user_id, :post_id, :comment)"
    comment_id = mysql.query_db(comment_insert_query, data)

    return redirect('/wall')

@app.route('/logout')
def getout():
    if 'user' in session:
        session.pop('user')
    if 'name' in session:
        session.pop('name')

    return redirect ('/')

app.run(debug=True)
