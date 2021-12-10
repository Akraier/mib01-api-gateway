from datetime import date, datetime
from flask import Blueprint, render_template, request
from flask.wrappers import Response
from werkzeug.utils import redirect 



from mib.auth.auth import current_user
import json
home = Blueprint('home', __name__)

_new_msg=0

#home page
@home.route('/')
def index():
    if current_user is not None:
        welcome = "Logged In!"
    else:
        welcome = None
    return render_template("index.html", welcome=welcome,new_msg=_new_msg)
