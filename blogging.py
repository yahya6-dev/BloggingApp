from app import create_app,db
from flask_migrate import Migrate
from app.models import User,Role,Post,Comment

app = create_app("development")
migrate = Migrate(app,db)

@app.shell_context_processor
def make_context():
	return dict(User=User,Role=Role,db=db,Post=Post,Comment=Comment)

@app.cli.command()
def test():
	import unittest
	tests = unittest.TestLoader().discover("tests")
	unittest.TextTestRunner(verbosity=5).run(tests)
  
