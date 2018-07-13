from flask import Flask, render_template, redirect, request, session, flash
import re
app = Flask(__name__)
from mysqlconnection import connectToMySQL
app.secret_key = "almondmilk"
mysql = connectToMySQL("emailVal")

@app.route('/')
def index():
    # identify whether the user has a session with us
    if 'submitted' not in session:
        session['submitted'] = False 

    return render_template("index.html")

@app.route('/submit', methods=['post'])
def validateEmail():
    print("yay", request.form)
    # check for empty fields
    emailRegex = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
    if len(request.form['email']) < 1:
        print("no email was provided")
        flash("Email must be provided")
    # the provided email does not match the expected pattern
    elif not emailRegex.match(request.form['email']):
        flash("Invalid email")
    # something was provided and it matched the email pattern
    else: 
    # check if it exists in the database already
    # 1. construct the query
        query = "SELECT * FROM emails WHERE email = %(user_email)s;"
    # 2. create a dictionary that has the keys that match the placeholders in the query
        data = { "user_email" : request.form['email'] }
        
        # store the result (an array) from talking to the database in the variable emails
        emails = mysql.query_db(query, data)

        print("here's what we got back from the database", len(emails))
        if len(emails) > 0: 
        # if an email comes back from the database, flash an error message
            flash("Email already exists!")
        else:
            # the email does not exist already, so insert it into the database
            query = "INSERT INTO emails (email, created_at, updated_at) VALUES (%(user_email)s, NOW(), NOW());"
            data = { "user_email" : request.form['email']}
            email = mysql.query_db(query, data)
            session['submitted'] = True
            flash(f"The email address you entered, {request.form['email']}, is a VALID email address! Thank you!")
            return redirect("/success")

    return redirect("/")

@app.route('/success')
def success():
    if 'submitted' in session and session['submitted'] == True:
        return render_template("success.html", emails=mysql.query_db("SELECT * FROM emails;"))
    else:
        flash("naughty naughty naughty you must provide an email to be allowed to see that page")
        return redirect('/')

@app.route("/logout")
def logout():
    session.clear()
    return redirect('/')

# emailregex = r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$'
#  emailRegex = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
if __name__ == "__main__":
    app.run(debug=True)