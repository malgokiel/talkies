from flask_sqlalchemy import SQLAlchemy
from flask import Flask, session, request, render_template, redirect, jsonify
import os
from data_models import db, User, Movie, UserMovies
from sql_data_manager import SQLiteDataManager
from interface import DataManagerInterface as interface
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helper import login_required
import helper
import os
import sys
from dotenv import load_dotenv
import requests
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import UnmappedInstanceError

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

            is_valid, message = helper.validate_registration(name, login, manager.get_all_users(), password, repeated_psw)
            if is_valid:
                hash = generate_password_hash(password, method="pbkdf2:sha256", salt_length=16)

                new_user = User(name=name,
                                login=login,
                                hash=hash
                                )
                manager.add_user(new_user)
                message = ["User successfully registered. Please log in."]
                return render_template("login.html", messages=message)
            else:
                return render_template("register.html", messages=message)

    return render_template("register.html")


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    
    if request.method == 'POST':
        all_movies = manager.get_all_movies()
        action = request.form.get('add_movie')
        search = request.form.get('search')
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

                if helper.is_new_movie(imdb_id, all_movies):
                    new_movie = Movie(title=title,
                                    director=director,
                                    year=year,
                                    rating=rating,
                                    poster_url=poster_url,
                                    imdb_id=imdb_id)
                    movie_id = manager.add_movie(new_movie)
                else:
                    movie = db.session.query(Movie).filter(Movie.imdb_id==imdb_id).first()
                    movie_id = movie.id
                try:
                    manager.add_user_movie(session["user_id"], movie_id)
                except IntegrityError:  
                    db.session.rollback()
                    user_movies = manager.get_user_movies(session["user_id"])
                    return render_template('index.html', movies=user_movies, messages="You already have this movie in your list")
        if search:
            print(search)
            matching_movies = manager.get_matching_movies(search, session["user_id"])
            if matching_movies:
                return render_template('index.html', movies=matching_movies)
            else:
                return render_template("index.html", movies=[], message="Oops, no matches found")
    user_movies = manager.get_user_movies(session["user_id"])
    return render_template('index.html', movies=user_movies)


@app.route('/add_movie', methods=['GET', 'POST'])
@login_required
def add_movie():
        pass


@app.route('/movie/<int:movie_id>', methods=['GET'])
@login_required
def movie_details(movie_id):
        movie = db.session.query(Movie).filter(Movie.id==movie_id).first()
        user_movie = db.session.query(UserMovies).filter(UserMovies.user_id==session['user_id'], UserMovies.movie_id==movie_id).first()
        return render_template('movie.html', movie=movie, user_movie=user_movie)


@app.route('/update_rating', methods=['POST'])
@login_required
def user_rating():
    data = request.get_json()
    movie_id = data.get('movie_id')
    rating = data.get('rating')
    print(f"Received rating update for movie ID: {movie_id}, New Rating: {rating}")
    manager.manage_user_rating(session["user_id"], movie_id, rating)
    return jsonify({'message': 'Rating updated successfully'}), 200


@app.route('/update_review', methods=['POST'])
@login_required
def user_review():
    data = request.get_json()
    movie_id = data.get('movie_id')
    review = data.get('review')
    print(f"Received review update for movie ID: {movie_id}, New Review: {review}")
    manager.manage_user_review(session["user_id"], movie_id, review)
    return jsonify({'message': 'Rating updated successfully'}), 200


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    session.clear()
    if request.method == 'POST':
        action = request.form.get('login')
        if action == 'login_user':
            user_login = request.form.get('login_id')
            password = request.form.get('password')
            matching_user = db.session.query(User).filter(User.login==user_login).all()
            if matching_user:
                user_hash = [user.hash for user in matching_user]
                user_id = [user.id for user in matching_user]
                if check_password_hash(user_hash[0], password):
                    session['user_id'] = user_id[0]
                    session['username'] = user_login
                    return redirect('/')
            else:
                return render_template("login.html", message="Incorrect user or password")

    return render_template("login.html")


@app.route("/movie/delete/<int:movie_id>", methods=['GET'])
@login_required
def delete_movie(movie_id):
    try:
        manager.delete_movie(session['user_id'], movie_id)
    except UnmappedInstanceError:
        print("Someobody just manually changed movie ID in HTML to a non existing user_movie relationship.")
    return redirect("/")


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