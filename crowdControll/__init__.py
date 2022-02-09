from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from multiprocessing import Queue
from flask_mail import Mail


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
app.config['SECRET_KEY'] = 'SECRET_KEY'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db?check_same_thread=False'
app.config['MAIL_SERVER'] = 'EMAIL_SERVER'
app.config['MAIL_PORT'] = 0
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'EMAIL_LOGIN'
app.config['MAIL_PASSWORD'] = 'EMAIL_PASSWORD'
mail = Mail(app)

db = SQLAlchemy(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

queue = Queue()

from crowdControll import routes
