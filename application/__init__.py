from flask import Flask,render_template,request
from flask_sqlalchemy import SQLAlchemy
import os
#from flask_login import LoginManager
from config import Config




app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config.from_object(Config)

db=SQLAlchemy(app)
# login_manager = LoginManager()
# login_manager.init_app(app)

from application import routes,models
