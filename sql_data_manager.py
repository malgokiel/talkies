from flask_sqlalchemy import SQLAlchemy
from interface import DataManagerInterface

class SQLiteDataManager(DataManagerInterface):
    """
    CLass responsible for reading the data source 
    and providing methods for data manipulation.
    """
    def __init__(self, db_file_name):
        self.db = SQLAlchemy(db_file_name)

    def get_all_users():
        """
        Returns a list of all users from a DB
        """
        pass

    def get_user_movies(user_id):
        """
        Returns a list of movies of a specific user
        """
        pass

    def add_user(user):
        """
        Adds a new user to the DB
        """
        pass

    def add_movie(movie):
        """
        Adds a new movie to the SB
        """
        pass

    def update_movie(movie):
        """
        Updates details of the specific movie in the DB
        """
        pass

    def delete_movie(movie_id):
        """
        Deletes a movie from DB based on it's id
        """
