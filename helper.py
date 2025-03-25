from flask import redirect, render_template, session
from functools import wraps


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
    error_messages = []

    if not password: 
        error_messages.append("password is required")
    if not repeated_psw or password != repeated_psw:
        error_messages.append("passwords do not match")
    if len(password) < 5 or password.isalpha() or password.isdigit():
        error_messages.append("password requirements: at least 5 characters long, must contain at least one number and at least one letter.")
    
    if error_messages:
        return error_messages
    else:
        return []
    
def validate_username(name, login, users):
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

    if validate_password(password, repeated_psw) == [] and validate_username(name, login, users) == []:
        return True, []
    else:
        messages = validate_password(password, repeated_psw) + validate_username(name, login, users)
        return False, messages


