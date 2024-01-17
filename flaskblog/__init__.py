from flask import Flask
from flask_sqlalchemy import SQLAlchemy           #sqlalchemy is database class
from flask_bcrypt import Bcrypt                   #bcrypt class generates the encrypts the password to a string so it becomes more secure
from flask_login import LoginManager              #this package is used to handle the login & logout of the user
from flask_mail import Mail

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a3749f956d14f0a6cea57d3302ff7c27'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)                                      #instance of SQLAlchemy class
bcrypt = Bcrypt(app)                                      #instance of Bcrypt class
login_manager = LoginManager(app)                         #instance of LoginManager class
login_manager.login_view = 'login'                         #If a user is not authenticated, they will be redirected to the login page.
login_manager.login_message_category = 'info'              #styles the message for login with help of bootstrap class 'info'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'uzerqazi028@gmail.com'
app.config['MAIL_PASSWORD'] = 'ohby jkll lfvf eoge'
mail = Mail(app)

from flaskblog import routes