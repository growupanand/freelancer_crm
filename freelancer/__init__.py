from flask import Flask, render_template, request, session
from bson import ObjectId

app = Flask(__name__)
app.secret_key = 'this is secret key'

from . import views
from . import controllers
from . import models