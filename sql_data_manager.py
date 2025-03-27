from sqlalchemy.exc import OperationalError
from data_models import Movie, User, UserMovies 
from interface import DataManagerInterface

class SQLiteDataManager(DataManagerInterface):
    """
    CLass responsible for reading the data source 
    and providing methods for data manipulation
    """
    def __init__(self, db):
        self.db = db


    def get_all_users(self):
        """
        Returns a list of all users from a DB
        """
        try:
            users = self.db.session.query(User).all()
            return users
        except OperationalError as e:
            print(e)
            return ["An error occured when quering DB. Please contact your administrator."]


    def get_all_movies(self):
        """
        Returns a list of all movies from a DB
        """
        movies = self.db.session.query(Movie).all()
        return movies

    def get_matching_user(self, user_login):

        matching_user = self.db.session.query(User).filter(User.login==user_login).all()
        return matching_user
    
    def get_matching_movies(self, find_match, user_id):
        """
        Returns a list of all movies in the user's library 
        which match (casefold) search criteria
        """
        user_movies = self.get_user_movies(user_id)
        matching_movies = [user_movie 
                           for user_movie 
                           in user_movies 
                           if find_match.casefold() in user_movie.title.casefold() 
                           or find_match.casefold() in user_movie.director.casefold()]
        return matching_movies


    def get_user_movies(self, user_id):
        """
        Returns a list of all movies added by a specific user
        to their library
        """
        try:
            users_movies = self.db.session.query(UserMovies).filter(UserMovies.user_id==user_id).all()
            ids = [UserMovies.movie_id for UserMovies in users_movies]
            movies = self.db.session.query(Movie).filter(Movie.id.in_(ids)).all()
            return movies
        except OperationalError as e:
            print(e)
            return ["An error occured when quering DB. Please contact your administrator."]


    def add_user(self, user):
        """
        Adds a new user to the DB
        """
        return self._add_to_db(user)


    def add_movie(self, movie):
        """
        Adds a new movie to the DB
        """
        self._add_to_db(movie)
        return movie.id
    

    def manage_user_review(self,user_id, movie_id, review):
        """
        Commits a new/updated user's review to DB
        """
        user_movie = self.db.session.query(UserMovies).filter(UserMovies.user_id==user_id, UserMovies.movie_id==movie_id).first()
        user_movie.user_review = review
        self.db.session.commit()


    def manage_user_rating(self,user_id, movie_id, rating):
        """
        Commits a new/updated user's rating to DB
        """
        user_movie = self.db.session.query(UserMovies).filter(UserMovies.user_id==user_id, UserMovies.movie_id==movie_id).first()
        user_movie.user_rating = rating
        self.db.session.commit()


    def add_user_movie(self, user_id, movie_id):
        """
        Adds a new user-movie relationship to DB
        """
        new_relationship = UserMovies(user_id=user_id,
                                      movie_id=movie_id,
                                      user_rating= 0,
                                      user_review= "no review")
        self._add_to_db(new_relationship)


    def delete_movie(self, user_id, movie_id):
        """
        Deletes a user-movie relationshop from DB based on their ids
        """
        user_movie = self.db.session.query(UserMovies).filter(UserMovies.user_id==user_id, UserMovies.movie_id==movie_id).first()
        self.db.session.delete(user_movie)
        self.db.session.commit()
        return "Movie deleted"
    

    def _add_to_db(self, new_item):
        """
        Adds and commits a new item to DB
        """
        try:
            self.db.session.add(new_item)
            self.db.session.commit()
            return ["Successfully added."]
        except ConnectionError:
            return ["Database connection error occurred. "
            "If the problem persist, contact your administrator."]


