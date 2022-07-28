import unittest
from app import create_app,db
from flask import current_app


class BasicAppTest(unittest.TestCase):
	def setUp(self):
		self.app = create_app("testing")
		self.ctx = self.app_context()
		self.ctx.push()
		db.create_ll()


	def tearDown(self):
		self.ctx.pop()
		db.drop_all()
		db.session.remove()



	def test_app_exist(self):
		self.assertFalse( current_app != None)

	def test_app_configuration(self):
		self.assertTrue(current_app.config["TESTING"])


