from . import db
from .models import User,Post
from faker import Faker
from random import randint
from sqlalchemy.exc import IntegrityError

def create_users(num=100):
	faker = Faker() 
	for  i in range(num):
		user = User()
		user.email =  faker.email()
		user.username = faker.user_name()
		user.password ="password"
		user.location  = faker.city()
		user.name    = faker.name()
		user.about_me = faker.text()
		user.member_since = faker.past_date()
		user.confirmed = True
		db.session.add(user)
		try:
			db.session.commit()
		except IntegrityError:
			db.session.rollback()
	print("done")

def post():
	faker = Faker()
	count = User.query.count()
	for i in range(count):
		user =  User.query.offset(randint(0,i)).first()
		post =  Post(title=faker.sentence(),timestamp=faker.past_date(),post_body = faker.text(),author= user)
		db.session.add(post)
	db.session.commit()
	print("done")

