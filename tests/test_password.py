import unittest
from app.models import User


class BasicPasswordTest(unitttest):
	def test_password_exist(self):
		user = User()
		user.password = "cat" 

		self.assertFalse(user.password_hash == None)

	def test_password_unreadable(self):
		user = User()
		user.password = "dog"
		with self.assertRaises(AttributeError):
			user.password


	def test_password_verify(self):
		user = User()
		user.password ="cat"
		self.assertTrue(user.verify("cat"))
		self.assertFalse(user.verify("dog"))

	def test_pass_hashing(self):
		user = User()
		user1 = User()
		user.password ="cat"
		user1.password = "cat"
		self.assertTrue(user.password_hash != user1.password_hash )
