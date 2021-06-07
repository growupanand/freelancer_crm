from flask import Flask, session
from functools import wraps
from models import User
from bson import ObjectId


app = Flask(__name__)
app.secret_key = 'this is secret'

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return views.login()
    return wrap

import views
import controller


if __name__ == '__main__':
    app.run()
