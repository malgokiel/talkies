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

    def get_all_users(self):
        """
        Returns a list of all users from a DB
        """
        users = self.db.session.query(User).all()
        return users

    def get_all_movies(self):
        movies = self.db.session.query(Movie).all()
        return movies

    def get_matching_movies(self, find_match, user_id):
        #movies = self.db.session.query(Movie).filter(or_(Movie.title.like(f"%{find_match}"), Movie.director.like(f"%{find_match}")))
        user_movies = self.get_user_movies(user_id)
        matching_movies = [user_movie for user_movie in user_movies if find_match.casefold() in user_movie.title or find_match.casefold() in user_movie.director]
        return matching_movies

    def get_user_movies(self, user_id):
        """
        Returns a list of movies of a specific user
        """
    
        users_movies = self.db.session.query(UserMovies).filter(UserMovies.user_id==user_id).all()
        ids = [UserMovies.movie_id for UserMovies in users_movies]
        movies = self.db.session.query(Movie).filter(Movie.id.in_(ids)).all()
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
        return movie.id
    

    def manage_user_review(self,user_id, movie_id, review):
        user_movie = self.db.session.query(UserMovies).filter(UserMovies.user_id==user_id, UserMovies.movie_id==movie_id).first()
        user_movie.user_review = review
        self.db.session.commit()


    def manage_user_rating(self,user_id, movie_id, rating):
        user_movie = self.db.session.query(UserMovies).filter(UserMovies.user_id==user_id, UserMovies.movie_id==movie_id).first()
        user_movie.user_rating = rating
        self.db.session.commit()

    def add_user_movie(self, user_id, movie_id):
        new_relationship = UserMovies(user_id=user_id,
                                      movie_id=movie_id,
                                      user_rating= None,
                                      user_review= None)
        
        self.db.session.add(new_relationship)
        self.db.session.commit()


    def delete_movie(self, user_id, movie_id):
        """
        Deletes a movie from DB based on it's id
        """
        #needs refactoring - we are not going to delete a movie from movies, 
        #we are going to delete a relationship movie-user from user_movies
        user_movie = self.db.session.query(UserMovies).filter(UserMovies.user_id==user_id, UserMovies.movie_id==movie_id).first()
        self.db.session.delete(user_movie)
        self.db.session.commit()
        return "Movie deleted"

