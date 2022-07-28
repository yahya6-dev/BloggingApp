import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
	SECRET_KEY  = os.environ.get("SECRET_KEY") or "hard to guess string"
	MAIL_SERVER = os.environ.get("MAIL_SERVER") or "smtp.gmail.com"
	MAIL_PORT   = 587

	MAIL_USERNAME = os.environ.get("MAIL_USERNAME") or "yahyasaid9350@gmail.com"
	MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD") or "hornet1350"
	MAIL_USE_TLS  = True

	BLOGGING_ADMIN = os.environ.get("BLOGGIN_ADMIN") or "yahyasaid9350@gmail.com"

	SQLALCHEMY_TRACK_MODIFICATIONS = False
	BLOGGING_MAIL_SUBJECT_PREFIX = "[BLOGGING]"

	@staticmethod
	def  init_app(app): pass


class DevelopmentConfig(Config):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URI") or "sqlite:///"+os.path.join(basedir,"dev-database.sqlite")


class TestingConfig(Config):
	TESTING =True
	SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URI") or "sqlite://"


class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI") or "sqlite:///"+os.path.join(basedir,"database.sqlite")


config = {
	"development":DevelopmentConfig,
	"testing":TestingConfig,
	"production":ProductionConfig,
	"default":DevelopmentConfig
}


