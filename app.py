from flask_sqlalchemy import SQLAlchemy
from flask import Flask, session, request, render_template, redirect
import os
from data_models import db, User, Movie, UserMovies
from sql_data_manager import SQLiteDataManager
from interface import DataManagerInterface as interface
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helper import login_required
# Set the app up and establish db connection

current_directory = os.getcwd()
database_path = os.path.join(current_directory, 'data', 'talkies.sqlite')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:////{database_path}'
db = SQLAlchemy(app)
manager = SQLiteDataManager(db)



# Configures session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Ensures the user always sees the most recent version
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route('/register', methods=['GET', 'POST'])
def register_new_user():

    if request.method == 'POST':
        action = request.form.get('add')
        if action == 'add_user':
            name = request.form.get('user_name')
            login = request.form.get('login')
            password = request.form.get('password')
            repeated_psw = request.form.get('repeated_psw')
        # validate with helper
            hash = generate_password_hash(password, method="pbkdf2:sha256", salt_length=16)

            new_user = User(name=name,
                            login=login,
                            hash=hash
                            )
            manager.add_user(new_user)
        return render_template("login.html")

    return render_template("register.html")


@app.route('/', methods=['GET'])
@login_required
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    session.clear()
    if request.method == 'POST':
        action = request.form.get('login')
        if action == 'login_user':
            user_login = request.form.get('login_id')
            password = request.form.get('password')
            matching_user = db.session.query(User).filter(User.login==user_login).all()
            user_hash = [user.hash for user in matching_user]
            user_id = [user.id for user in matching_user]
            if check_password_hash(user_hash[0], password):
                session['user_id'] = user_id[0]
                session['username'] = user_login
                return redirect('/')
            else:
                print("here")

    return render_template("login.html")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    """Logs the user out"""

    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)


# user = User(name='Kasia',
#             login='Kasia123',
#             hash='xsdff01')

# with app.app_context():
#     print(manager.add_user(user))



# with app.app_context():
#    db.create_all()