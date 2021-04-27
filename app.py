from flask import Flask, redirect, url_for, render_template, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///User.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SECRET_KEY'] =  'supersupesupersecret'# this has cookies data etc..

db = SQLAlchemy(app) # database

class User(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(50), nullable=False)
    email = db.Column("email", db.String(90), nullable=False)
    password = db.Column("password", db.String(120), nullable=False)

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
        submit_name = request.form.get('new_name') # assigning information that the player has submitted onto variables
        submit_pass = request.form.get('new_pass')
        submit_email = request.form.get('new_email')
        
        if len(submit_name) == 0 or len(submit_email) == 0 or len(submit_pass) == 0:
            flash("Please fill out the whole form")
            return render_template("register.html")

        if len(User.query.filter_by(password=submit_name).all()) > 0:
            flash("Username already exists")
            return redirect(url_for("register"))

        if len(User.query.filter_by(email=submit_email).all()) > 0:
            flash("Pmail is already registered, please use another one")
            return redirect(url_for("register"))
        
        else:
            print("before hashing: " + submit_pass) 
            submit_pass = generate_password_hash(submit_pass) 
            # hashing password before adding it to the database
            print("after hashing: " + submit_pass)

            new_user = User(submit_name, submit_email, submit_pass) # creating a new user (not adding password directly, instead, it will be hashed before adding)

            db.session.add(new_user) # adding user to database
            db.session.commit() # commit changes to the database

            flash("User " + submit_name + " has been registered! You can now log in.")
            return redirect(url_for("login"))

    else: # --> if the user has connected to the website (GET)
        return render_template("register.html")

@app.route("/login/", methods=["POST", "GET"])
def login():
    if "active_username" in session:
        
        flash("You are already logged in!")
        return redirect(url_for("index"))

    if request.method == 'POST':
        input_name = request.form.get('input_name')
        input_pass = request.form.get('input_pass')

        found_user_by_name = User.query.filter_by(name=input_name).first() 

        if found_user_by_name:
            found_user_by_name = User.query.filter_by(name=input_name).first() 
            # if submitted name exists in database, it is True (or else, False)
        else:
            flash("Could not find any user with that name.")
            return redirect(url_for("login"))

        is_input_pass_correct = check_password_hash(found_user_by_name.password, input_pass) 
        # True or False, depending on if the passwords match

#        print(found_user_by_name.password,"+", input_pass, "=", is_input_pass_correct)

        if len(input_name) == 0 or len(input_pass) == 0:
            flash("Please type your name and password!")
                    
            return redirect(url_for("login"))
        else:
            if found_user_by_name and is_input_pass_correct: 
            # if a user username exists in database and input
            # password matches with found user's hashed password
                session['active_username'] = found_user_by_name.name
                session['active_userpassword'] = found_user_by_name.password
                session['active_useremail'] = found_user_by_name.email

                flash("The login was successful")

                return redirect(url_for("index"))
            else:
                flash("The username or password combination is incorrect!")
                
                return redirect(url_for("login"))
    else:
        return render_template("login.html") 
        # here we return html. It can also be a html template.

@app.route("/logout/")
def logout():
    # delete all session data from the user
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

        flash("Hey! You are currently logged in as " + active_username + "!")

    return render_template("viewtables.html", values=User.query.all())

@app.route("/deluser/", methods=["POST", "GET"])
def deluser():
    if request.method == "POST":
        deletesingleuser = request.form.get("deleteone")
        deleteallusers = request.form.get("deleteall")

        if deletesingleuser:
            deleteduser = request.form.get("deleteduser")
            checkuser = User.query.filter_by(name=deleteduser).first()

            try:
                db.session.delete(checkuser)
                db.session.commit()
                flash("user has been deleted")
                return redirect(url_for("deluser"))

            except:
                flash("there are no users to delete")
                return redirect(url_for("deluser"))

        elif deleteallusers:
            User.query.delete()
            db.session.commit()
            flash("all users have been deleted")
            return redirect(url_for("deluser"))

        else:
            flash("could not find any user(s)...")
    else:
        return render_template("deluser.html")
    
if __name__ == "__main__": 
    # __name__ == "__main__" means:
    # only if we run this file directly, we will run the app
    # not if we f.ex. import this file from another file.
    db.create_all()
    app.run(debug=True)