from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """
    Class responsible for creating a user with their individual attributes
    """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    login = db.Column(db.String)
    hash = db.Column(db.String)

    def __repr__(self):
        return f'username: {self.name}, user_id: {self.id}, hash: {self.hash}'
    

class Movie(db.Model):
    """
    Class responsible for creating a movie with its individual attributes
    """

    __tablename__ = 'movies'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    director = db.Column(db.String)
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    poster_url = db.Column(db.String)
    imdb_id = db.Column(db.String)

    def __repr__(self):
        return f'"{self.title} ({self.year}) directed by {self.director}. Rating: {self.rating}"'


class UserMovies(db.Model):
    """
    Class responsible for creating a movie-user relationship.
    Based on this relationship movies are fetched from movies table
    for the specific user
    """

    __tablename__ = 'user_movies'

    user_id = db.Column(db.Integer, db.ForeignKey(User.__table__.c.id), primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey(Movie.__table__.c.id), primary_key=True)
    user_rating = db.Column(db.String)
    user_review = db.Column(db.String)

    def __repr__ (self):
        return f'User: {self.user_id}, Movie: {self.movie_id}'
    
