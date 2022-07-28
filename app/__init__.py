from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask_bootstrap import Bootstrap5
from flask_mail import Mail
from config import config
from flask_pagedown import PageDown

pagedown = PageDown()
db = SQLAlchemy()
moment = Moment()
login_manager = LoginManager()
bootstrap = Bootstrap5()
mail = Mail()

login_manager.login_view = "auth.login"


def create_app(config_name):
	app = Flask(__name__)
	app.config.from_object(config[config_name])

	config[config_name].init_app(app)
	from .auth import auth
	from .main import main
	app.register_blueprint(main)
	app.register_blueprint(auth,url_prefix="/auth")
	pagedown.init_app(app)
	db.init_app(app)
	moment.init_app(app)
	bootstrap.init_app(app)
	mail.init_app(app)
	login_manager.init_app(app)

	return app 
