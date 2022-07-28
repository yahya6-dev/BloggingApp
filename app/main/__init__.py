from flask  import Blueprint
from ..models import Permission,Post

main = Blueprint("main",__name__)

from . import views

@main.app_context_processor
def inject_context():
	return dict(Permission=Permission,Post=Post)
