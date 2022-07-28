import unittest
from app.models import User


class TestGravatar(unittest.TestCase):
	def test_email_hash(self):
		user = User()
		user.email =  "badboy@hornet.com"
		user.email_hash = user.gravatar_hash()
		self.assert

	def test_gravatar(self):
