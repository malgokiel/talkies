import os
from flask import Flask, jsonify, request, render_template, redirect, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import UnmappedInstanceError

from data_models import db, User, Movie, UserMovies
from sql_data_manager import SQLiteDataManager
import helper
from helper import login_required


# Set the app up and establish db connection
current_directory = os.getcwd()
database_path = os.path.join(current_directory, 'data', 'talkies.sqlite')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:////{database_path}'
db = SQLAlchemy(app)
manager = SQLiteDataManager(db)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Ensure the user always sees the most recent version
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route('/register', methods=['GET', 'POST'])
def register_new_user():
    """
    Fetches information from a html form 
    and uses them to create a new User instance.
    """
    if request.method == 'POST':
        action = request.form.get('add')
        if action == 'add_user':
            name = request.form.get('user_name')
            login = request.form.get('login')
            password = request.form.get('password')
            repeated_psw = request.form.get('repeated_psw')

            is_valid, message = helper.validate_registration(name, 
                                                             login, 
                                                             manager.get_all_users(), 
                                                             password, 
                                                             repeated_psw)
            if is_valid:
                hash = generate_password_hash(password, method="pbkdf2:sha256", salt_length=16)
                
                new_user = User(name=name,
                                login=login,
                                hash=hash)
                
                message = manager.add_user(new_user)

                return render_template("login.html", messages=message)
            else:
                return render_template("register.html", messages=message)

    return render_template("register.html")


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """
    Fetches all movies added by the user and displays them.
    Allows the user to search throuygh their library
    and to add a new movie
    """
    if request.method == 'POST':
        all_movies = manager.get_all_movies()

        action = request.form.get('add_movie')
        search = request.form.get('search')

        if action == 'add':
            title_to_search = request.form.get('title')
            
            # gets movie data from api
            is_success, movie_json = helper.get_movie_from_api(title_to_search)
            if is_success:
                if movie_json["Response"] == 'True' and movie_json["Type"] != "series":
                    title = movie_json["Title"]
                    director = movie_json["Director"]
                    year = movie_json["Year"]
                    rating = movie_json["imdbRating"]
                    poster_url = movie_json["Poster"]
                    imdb_id = movie_json["imdbID"]
                    
                    # if it's a new movie adds it to the table, else
                    # just gets it's existing id
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

                    # adds new user movie relationship if it does not yet exist
                    try:
                        manager.add_user_movie(session["user_id"], movie_id)
                    except IntegrityError:  
                        db.session.rollback()
                        user_movies = manager.get_user_movies(session["user_id"])
                        return render_template('index.html', movies=user_movies, messages=["You already have this movie in your list"])
            else:
                return render_template('index.html', movies=user_movies, messages=movie_json)
        
        if search:
            matching_movies = manager.get_matching_movies(search, session["user_id"])
            if matching_movies:
                return render_template('index.html', movies=matching_movies)
            else:
                return render_template("index.html", movies=[], message=["Oops, no matches found"])

    user_movies = manager.get_user_movies(session["user_id"])
    return render_template('index.html', movies=user_movies)


@app.route('/add_movie', methods=['GET', 'POST'])
@login_required
def add_movie():
        pass


@app.route('/movie/<int:movie_id>', methods=['GET'])
@login_required
def movie_details(movie_id):
    """
    Displays information about the queried movie.
    """
    movie = db.session.query(Movie).filter(Movie.id==movie_id).first()
    user_movie = db.session.query(UserMovies).filter(UserMovies.user_id==session['user_id'], UserMovies.movie_id==movie_id).first()
    return render_template('movie.html', movie=movie, user_movie=user_movie)


@app.route('/update_rating', methods=['POST'])
@login_required
def user_rating():
    """
    Allows the user to add/edit their own rating
    """
    data = request.get_json()
    movie_id = data.get('movie_id')
    rating = data.get('rating')
    try:
        rating = float(rating)
    except ValueError:
        return jsonify({'message': 'Rating is not a number'}), 400
    
    manager.manage_user_rating(session["user_id"], movie_id, rating)
    return jsonify({'message': 'Rating updated successfully'}), 200


@app.route('/update_review', methods=['POST'])
@login_required
def user_review():
    """
    Allows the user to add/edit their own rating
    """
    data = request.get_json()
    movie_id = data.get('movie_id')
    review = data.get('review')
    print(f"Received review update for movie ID: {movie_id}, New Review: {review}")
    manager.manage_user_review(session["user_id"], movie_id, review)
    return jsonify({'message': 'Rating updated successfully'}), 200


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    """
    Validates user login details and logs the user in if correct
    """
    session.clear()
    if request.method == 'POST':
        action = request.form.get('login')
        if action == 'login_user':
            user_login = request.form.get('login_id')
            password = request.form.get('password')
            matching_user = manager.get_matching_user(user_login)
            if matching_user:
                user_hash = [user.hash for user in matching_user]
                user_id = [user.id for user in matching_user]
                if check_password_hash(user_hash[0], password):
                    session['user_id'] = user_id[0]
                    session['username'] = user_login
                    return redirect('/')
            else:
                return render_template("login.html", message=["Incorrect user or password"])

    return render_template("login.html")


@app.route("/movie/delete/<int:movie_id>", methods=['GET'])
@login_required
def delete_movie(movie_id):
    """
    Deletes a user-movie relationship from a table.
    At the moment leaves the movie in the table in case other users are connected to it.
    """
    try:
        manager.delete_movie(session['user_id'], movie_id)
    except UnmappedInstanceError:
        print("Someobody just manually changed movie ID in HTML to a non existing user_movie relationship.")
    return redirect("/")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    """
    Logs the user out
    """
    session.clear()
    return redirect("/")


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)



# user = User(name='Kasia',
#             login='Kasia123',
#             hash='xsdff01')

# with app.app_context():
#     print(manager.add_user(user)

# with app.app_context():
#     db.create_all() 