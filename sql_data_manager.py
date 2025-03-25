from flask_sqlalchemy import SQLAlchemy
from interface import DataManagerInterface
from data_models import User, Movie, UserMovies 
from sqlalchemy import create_engine, text

class SQLiteDataManager(DataManagerInterface):
    """
    CLass responsible for reading the data source 
    and providing methods for data manipulation.
    """
    def __init__(self, db):
        self.db = db

    def get_all_users():
        """
        Returns a list of all users from a DB
        """
        users = User.query.all()
        return users


    def get_user_movies(user_id):
        """
        Returns a list of movies of a specific user
        """
        users_movies = UserMovies.query.filter(user_id=user_id).all()
        ids = [UserMovies.movie_id for UserMovies in users_movies]
        movies = Movie.query.filter(Movie.id.in_(ids)).all()
        return movies


    def add_user(self, user):
        """
        Adds a new user to the DB
        """
        self.db.session.add(user)
        self.db.session.commit()
        return "New user added"


    def add_movie(self, movie):
        """
        Adds a new movie to the SB
        """
        #Also appends the user_movies, 
        #first checks of movie exists or not
        self.db.session.add(movie)
        self.db.session.commit()
        return "New movie added"
    

    def update_user_movie(user_movie):
        """
        Updates details of the specific movie in the DB
        """
        #we don't update a movie because we get everything from IDBN
        #we are updating user-Movies

        # also needed: add_user_review(), add_user_rating()
        pass

    def add_user_review():
        pass

    def add_user_rating():
        pass

    def delete_movie(self, user_id, movie_id):
        """
        Deletes a movie from DB based on it's id
        """
        #needs refactoring - we are not going to delete a movie from movies, 
        #we are going to delete a relationship movie-user from user_movies
        movie_to_delete = self.db.session.get(Movie, movie_id)
        self.db.session.delete(movie_to_delete)
        self.db.session.commit()
        return "Movie deleted"

