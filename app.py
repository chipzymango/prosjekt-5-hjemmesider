from flask import Flask, redirect, url_for, render_template, request, flash, session
from flask_sqlalchemy import SQLAlchemy
 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///User.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SECRET_KEY'] =  'supersupesupersecret'# this has the cookie data etc..

db = SQLAlchemy(app) # database

class User(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(50), nullable=False)
    email = db.Column("email", db.String(50), nullable=False)
    password = db.Column("password", db.String(10), nullable=False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

# - normal sites that are available to everyone -

@app.route("/") # automatically redirects to this page (default)
def home():
    return render_template("index.html") # here we return html. It can also be a html template.

@app.route("/index/")
def index():
    return render_template("index.html")
    
@app.route("/about/")
def about():
    return render_template("about.html")

# - sites that involve authentication - 

@app.route("/register/", methods=["POST", "GET"])
def register():
    if request.method == 'POST': # --> if the user has pressed submit (POST)
        submit_name = request.form.get('new_name') # assigning information that the player has submitted onto a variable
        submit_pass = request.form.get('new_pass')
        submit_email = request.form.get('new_email')
        
        if len(submit_name) < 0 or len(submit_email) < 0 or len(submit_pass) < 0:
            flash("please fill out the whole form")
            return render_template("register.html")

        if len(User.query.filter_by(password=submit_pass).all()) > 0:
            flash("username already exists")
            return render_template("register.html")

        elif len(User.query.filter_by(email=submit_email).all()) > 0:
            flash("email is already registered, please use another one")
            return render_template("register.html")

        else:
            new_user = User(submit_name, submit_email, submit_pass) # creating a new user
            db.session.add(new_user) # adding user to database
            db.session.commit() # commit changes to the database

            flash("user " + submit_name + " has been registered! you can now log in...")
            return redirect(url_for("login"))

    else: # --> if the user has connected to the website (GET)
        return render_template("register.html")

@app.route("/login/", methods=["POST", "GET"]) 
def login():
    if "active_username" in session:

        return redirect(url_for("index"))

    if request.method == 'POST':
        submit_name = request.form.get('input_name')
        submit_pass = request.form.get('input_pass')
        
        found_username = User.query.filter_by(name=submit_name).first() # if submitted name == name in database then it is True (or else, False)
        found_userpassword = User.query.filter_by(password=submit_pass).first() # if submitted pass == pass in database then it is True (or else, False)
        if len(submit_name) == 0 or len(submit_pass) == 0:
            flash("please write your name and password!")
            
            return redirect(url_for("login"))
        else:
            if found_username and found_userpassword:
                session['active_username'] = found_username.name
                session['active_userpassword'] = found_userpassword.password
                session['active_useremail'] = found_username.email
                flash("login was successful")
                return redirect(url_for("login"))
            else:
                flash("The username or password combination is incorrect!")
                
                return redirect(url_for("login"))
    else:
        return render_template("login.html") # here we return html. It can also be a html template.

@app.route("/logout/")
def logout():
    session.pop("active_username", None)
    session.pop("active_userpassword", None)
    session.pop("active_useremail", None)

    flash("You are now logged out!")

    return redirect(url_for("index"))

# ----- not visible

@app.route("/viewusers/") 
def viewusers():
    if "active_username" in session:

        active_username = session["active_username"]

        flash("You are logged in as " + active_username)

    return render_template("viewtables.html", values=User.query.all())
    
if __name__ == "__main__": # only if we run this file directly, we will run the app, not if we import this file from another file.
    db.create_all()
    app.run(debug=True)