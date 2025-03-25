from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    login = db.Column(db.String)
    hash = db.Column(db.String)

    def __repr__(self):
        return f'username: {self.name}, user_id: {self.id}, hash: {self.hash}'
    

class Movie(db.Model):

    __tablename__ = 'movies'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    director = db.Column(db.String)
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)

    def __repr__(self):
        return f'"{self.title} ({self.year}) directed by {self.director}. Rating: {self.rating}"'

class UserMovies(db.Model):

    __tablename__ = 'user_movies'

    user_id = db.Column(db.Integer, db.ForeignKey(User.__table__.c.id), primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey(Movie.__table__.c.id), primary_key=True)
    user_rating = db.Column(db.String)
    user_review = db.Column(db.String)

    def __repr__ (self):
        return f'User: {self.user_id}, Movie: {self.movie_id}'
    
