from flask_sqlalchemy import SQLAlchemy
from flask import Flask, session, request, render_template, redirect
import os
from data_models import db, User, Movie, UserMovies
from sql_data_manager import SQLiteDataManager
from interface import DataManagerInterface as interface
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helper import login_required
import os
import sys
from dotenv import load_dotenv
import requests

load_dotenv()
API_KEY = os.getenv('API_KEY')

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


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        action = request.form.get('add_movie')
        if action == 'add':
            title_to_search = request.form.get('title')
            api_url = f'http://www.omdbapi.com/?apikey={API_KEY}&t={title_to_search}'

            try:
                response = requests.get(api_url)
                if response.status_code == 200:
                    title_data_json = response.json()
                else:
                    print(f"Error occurred: {response.status_code}")
                    sys.exit()
            except requests.exceptions.ConnectionError:
                print(
                    "We were not able to connect to www.omdbapi.com. "
                    "Please check your Internet connection or try again later.")
                sys.exit()
            
            if title_data_json["Response"] == 'True' and title_data_json["Type"] != "series":
                title = title_data_json["Title"]
                director = title_data_json["Director"]
                year = title_data_json["Year"]
                rating = title_data_json["imdbRating"]
                poster_url = title_data_json["Poster"]
                imdb_id = title_data_json["imdbID"]

                new_movie = Movie(title=title,
                                director=director,
                                year=year,
                                rating=rating,
                                poster_url=poster_url,
                                imdb_id=imdb_id)
                movie_id = manager.add_movie(new_movie)

                manager.add_user_movie(session["user_id"], movie_id)

    movies = manager.get_user_movies(session["user_id"])
    print(movies)
    return render_template('index.html', movies=movies)


@app.route('/add_movie', methods=['GET', 'POST'])
@login_required
def add_movie():
        pass


@app.route('/movie/<int:movie_id>', methods=['GET'])
@login_required
def movie_details(movie_id):
        print("function entered")
        movie = db.session.query(Movie).filter(Movie.id==movie_id).first()
        print("movie gotten")
        user_movie = db.session.query(UserMovies).filter(UserMovies.user_id==session['user_id'], UserMovies.movie_id==movie_id).first()
        print("got usermovie")
        return render_template('movie.html', movie=movie, user_movie=user_movie)


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
#     db.create_all()