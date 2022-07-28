from functools import wraps
from flask_login import current_user
from .models import Permission
from flask import abort

def permission_required(permission):
	def decorator(f):
		@wraps(f)
		def decorated_function(*args,**kargs):
			if not current_user.can(permission):
				abort(404)
			return f(*args,**kargs)
		return decorated_function
	return decorator


def admin_required(f):
	return  permission_required(Permission.ADMIN)(f)
