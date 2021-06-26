from flask import session
from bson import ObjectId

def get_user_id():
    return ObjectId(session['user']['_id'])