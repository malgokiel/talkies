import os
from functools import wraps
from dotenv import load_dotenv
import requests
from flask import redirect, session

# Get API KEY
load_dotenv()
API_KEY = os.getenv('API_KEY')

def login_required(f):
    """
    Login Required Decorator:
    https://flask.palletsprojects.com/en/3.0.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def validate_password(password, repeated_psw):
    """
    Validates if the password used during registration matches all requirements
    """
    error_messages = []

    if not password: 
        error_messages.append("password is required")
    if not repeated_psw or password != repeated_psw:
        error_messages.append("passwords do not match")
    if len(password) < 5 or password.isalpha() or password.isdigit():
        error_messages.append("password requirements: "
        "at least 5 characters long, "
        "must contain at least one number "
        "and at least one letter.")
    
    if error_messages:
        return error_messages
    else:
        return []
    

def validate_username(name, login, users):
    """
    Validates if the login used during registration matches all requirements
    and is unique
    """
    error_messages = []

    user_logins = [user.login for user in users]
    if not name:
        error_messages.append("name is required")
    if not login:
        error_messages.append("login is required")
    if login in user_logins:
        error_messages.append("this user already exists")
    
    if error_messages:
        return error_messages
    else:
        return []


def validate_registration(name, login, users, password, repeated_psw):
    """
    Validates if all fields in the registration form are correct and provided
    """
    try:
        valid_password = validate_password(password, repeated_psw)
        valid_user = validate_username(name, login, users)
    except AttributeError as e:
        print(e)
        return False, ["An error occured when quering DB. Please contact your administrator."]

    if valid_password == [] and valid_user == []:
        return True, []
    else:
        messages = valid_password + valid_user
        return False, messages


def is_new_movie(movie_imdb, movies):
    """
    Checks if the movie already exists in the DB
    """
    movie_imdb_ids = [movie.imdb_id for movie in movies]
    if movie_imdb in movie_imdb_ids:
        return False
    else:
        return True


def get_movie_from_api(title_to_search):
    api_url = f'http://www.omdbapi.com/?apikey={API_KEY}&t={title_to_search}'

    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            title_data_json = response.json()
            return True, title_data_json
        else:
            print(f"Error occurred: {response.status_code}")
    except requests.exceptions.ConnectionError:
        return False, ["We were not able to connect to www.omdbapi.com. "
        "Please try again later."]
