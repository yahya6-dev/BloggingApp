from . import db
from werkzeug.security import generate_password_hash,check_password_hash
from itsdangerous import TimedSerializer as Serializer
from flask_login import UserMixin,AnonymousUserMixin,login_required
from . import login_manager
from datetime import datetime
from flask import current_app,request
import hashlib
from markdown import markdown
import bleach

class Permission:
	FOLLOW  = 1
	COMMENT = 2
	WRITE   = 4
	MODERATE= 8
	ADMIN   = 16





@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))


likes = db.Table("likes",db.Column("users_id",db.Integer,db.ForeignKey("users.id")),
	db.Column("post_id",db.Integer,db.ForeignKey("posts.id"))

)

class Reply(db.Model):
	__tablename__="replies"
	id = db.Column(db.Integer,primary_key=True)
	author_id = db.Column(db.Integer,db.ForeignKey("users.id"))
	comment_id = db.Column(db.Integer,db.ForeignKey("comments.id"))
	reply  = db.Column(db.Text)
	timestamp = db.Column(db.DateTime,default=datetime.utcnow)
	disabled = db.Column(db.Boolean,default=False)



class Post(db.Model):
	__tablename__="posts"
	id = db.Column(db.Integer,primary_key=True)
	title = db.Column(db.String(68))
	post_body = db.Column(db.Text())
	post_html = db.Column(db.Text)
	timestamp = db.Column(db.DateTime,default=datetime.utcnow)
	author_id    = db.Column(db.Integer,db.ForeignKey("users.id"))
	category =  db.Column(db.Integer,default=0)
	comment_id = db.relationship("Comment",backref="post",lazy="dynamic")
	users_id = db.relationship("User",secondary=likes,backref=db.backref("user",lazy="dynamic"),lazy="dynamic")
	disabled = db.Column(db.Boolean,default=False)
	long_post  = db.Column(db.Boolean,default=False)


	def num_comments(self):
		return self.comment_id.count()
	def is_liking(self,user):
		return self.users_id.filter(User.id==user.id).first() != None

	def get_likes(self):
		return len(self.users_id.all())

	def add_like(self,user):
		if not self.is_liking(user):
			self.users_id.append(user)
			db.session.add_all([user,self])

	def unlike(self,user):
		if self.is_liking(user):
			u = self.users_id.filter_by(id=user.id).first()
			self.users_id.remove(u)
			db.session.add(self)

	@staticmethod
	def on_changed_body(target,new,old,initiator):
		allowed_tags = ["h3","code","abbr","strong","img","h4","i","b","h5","p","br"]
		target.post_html = bleach.linkify(bleach.clean(markdown(new,output_format="html"),tags=allowed_tags,strip=True))

db.event.listen(Post.post_body,"set",Post.on_changed_body)



class Comment(db.Model):
	__tablename__="comments"
	id = db.Column(db.Integer,primary_key=True)
	comment_body = db.Column(db.Text)
	comment_html = db.Column(db.Text)
	author_id  = db.Column(db.Integer,db.ForeignKey("users.id"))
	post_id    = db.Column(db.Integer,db.ForeignKey("posts.id"))
	timestamp = db.Column(db.DateTime,default=datetime.utcnow)
	disabled  = db.Column(db.Boolean,default=False)
	long_post  = db.Column(db.Boolean,default=False)
	replies   = db.relationship("Reply",backref="comment",lazy="dynamic") 

	@staticmethod
	def on_change_body(target,value,old,initiator):
		allowed_tags = ["code","strong","h1","pre","h2","abbr","mark"]
		target.body_html = bleach.linkify(bleach.clean(markdown(value,output_format="html"),tags=allowed_tags,strip=True))

db.event.listen(Comment.comment_body,"set",Comment.on_change_body)
class Follows(db.Model):
	__tablename__="follows"
	follower_id = db.Column(db.Integer,db.ForeignKey("users.id"),primary_key=True)
	followed_id = db.Column(db.Integer,db.ForeignKey("users.id"),primary_key=True)
	timestamp = db.Column(db.DateTime,default=datetime.utcnow)



class Role(db.Model):
	__tablename__="roles"
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(64),unique=True)
	default = db.Column(db.Boolean,index=True,default=True)
	permissions = db.Column(db.Integer)
	users = db.relationship("User",backref="role",lazy="dynamic")

	def __init__(self,**kargs):
		super(Role,self).__init__(**kargs)
		if self.permissions is None:
			self.permissions = 0


	def has_permission(self,permission):
		return self.permissions & permission == permission

	def add_permissions(self,permission):
		if not self.has_permission(permission):
			self.permissions += permission

	def remove_permissions(self,permission):
		if self.has_permission(permission):
			self.permissions -= permission

	def reset_permissions(self,permission):
		self.permissions = 0

	@staticmethod
	def insert_roles():
		roles = {"User":[Permission.FOLLOW,Permission.COMMENT,Permission.WRITE],
			"Moderate":[Permission.FOLLOW,Permission.COMMENT,Permission.WRITE,Permission.MODERATE],
			"Admin":[Permission.FOLLOW,Permission.COMMENT,Permission.WRITE,Permission.MODERATE,Permission.ADMIN]
		}

		default_role = "User"
		for r in roles:
			role = Role.query.filter_by(name=r).first()
			if role is None:
				role = Role(name=r)
			for permission in roles[r]:
				role.add_permissions(permission)
			role.default = default_role == r
			db.session.add(role)
		db.session.commit()


class AnonymousUser(AnonymousUserMixin):
	def can(self,permission):
		return False
	def is_administrator(self):
		return False

login_manager.anonymous_user = AnonymousUser

class User(UserMixin,db.Model):
	__tablename__="users"
	id = db.Column(db.Integer,primary_key=True)
	username = db.Column(db.String(64),index=True,unique=True)
	email    = db.Column(db.String(64),unique=True,index=True)
	password_hash = db.Column(db.String(128),unique=True,index=True)
	about_me  = db.Column(db.Text())
	location  = db.Column(db.String(64))
	member_since = db.Column(db.DateTime,default=datetime.utcnow)
	last_seen = db.Column(db.DateTime,default=datetime.utcnow())
	name = db.Column(db.String(64),index=True)
	confirmed = db.Column(db.Boolean,default=False)
	gender    = db.Column(db.String(12),index=True) 
	roles = db.Column(db.Integer,db.ForeignKey("roles.id"))
	email_hash = db.Column(db.String(32),index=True)
	posts = db.relationship("Post",backref="author",lazy="dynamic")
	followed = db.relationship("Follows",foreign_keys=[Follows.follower_id],backref=db.backref("follower",lazy="joined"),lazy="dynamic",cascade="all, delete-orphan")
	follower = db.relationship("Follows",foreign_keys=[Follows.followed_id],backref=db.backref("followed",lazy="joined"),lazy="dynamic",cascade="all, delete-orphan")
	comment_id = db.relationship("Comment",backref="author",lazy="dynamic") 
	about_me_html = db.Column(db.Text)
	blocked = db.Column(db.Boolean,default=False) 
	repliers_id = db.relationship("Reply",backref="user",lazy="dynamic")


	@staticmethod
	def on_changed_about(target,value,old,initiator):
		allowed_tags = ["code","strong","pre","i","b","br","h3","mark"]
		target.about_me_html = bleach.linkify(bleach.clean(markdown(value,output_format="html"),tags=allowed_tags,strip=True))



	def ping(self):
		self.last_seen = datetime.utcnow()
		db.session.add(self)
		db.session.commmit() 

	def __init__(self,**kargs):
		super(User,self).__init__(**kargs)
		if self.email != None and not self.email_hash:
			self.email_hash = self.gravatar()

		if self.role is None:
			if self.email == current_app.config["BLOGGING_ADMIN"]:
				self.role = Role.query.filter_by(name="Admin").first()
			else:
				self.role = Role.query.filter_by(default=True).first()


	def gravatar_hash(self):
		return hashlib.md5(self.email.encode("utf-8")).hexdigest()

	def gravatar(self,size=50,default="identicon",rating="g"):
		if request.is_secure:
			url = "https://secure.gravatar.com/avatar"
		else:
			url = "http://gravatar.com/avatar"
		hash = self.email_hash or self.gravatar_hash()

		return "{url}/{hash}?s={size}&d={default}&r={rating}".format(url=url,hash=hash,size=size,default=default,rating=rating)

	@property
	def password(self):
		raise AttributeError("password unreadable")

	@password.setter
	def password(self,password):
		self.password_hash  = generate_password_hash(password)

	def verify_password(self,password):
		return check_password_hash(self.password_hash,password)

	def generate_confirmation_token(self,expires_in=3600):
		s = Serializer(current_app.config["SECRET_KEY"],expires_in=expires_in)
		return s.dumps({"confirm":self.id}).decode("utf-8")

	def generate_pass_reset_token(self,password,expires_in=3600):
		s =  Serializer(current_app.config["SECRET_KEY"],expires_in=expires_in)
		return s.dumps({"confirm":self.id,"password":password})

	def is_following(self,user):
		if user.id is None:
			return False
		return self.followed.filter_by(followed_id = user.id).first() != None

	def is_followed_by(self,user):
		if user.id is None:
			return False
		return  self.follower.filter_by(follower_id= user.id).first() != None

	def follow(self,user):
		if not self.is_following(user):
			f = Follows(follower=self,followed=user)
			db.session.add(f)

	def unfollow(self,user):
		if self.is_following(user):
			u = self.followed.filter_by(followed_id  = user.id).first()
			if u: db.session.delete(u)
	def get_followers(self):
		return self.follower

	def num_followers(self):
		return len(self.follower.all())

	@property
	def followed_post(self):
		return db.session.query(Post).select_from(Follows).filter_by(follower_id=self.id).join(Post,Follows.followed_id==Post.author_id)

	def confirm(self,token):
		s = Serializer(current_app.config["SECRET_KEY"])
		try:
			data = s.loads(token).encode()
		except:
			pass
		else:
			if data.get("confirm") != self.id:
				return False
		if not self.confirmed:
			self.confirmed = True
		db.session.add(self)
		return True

	@staticmethod
	def confirm_user(token):
		s = Serializer(current_app.config["SECRET_KEY"])

		try:
			data = s.loads(token)
		except:
			return None
		u = User.query.get_or_404(data.get("confirm"))
		u.password = data.get("password") 
		db.session.add(u)
		return u
		
	def ping(self):
		self.last_seen = datetime.utcnow()
		db.session.add(self)
		db.session.commit()


	def can(self,permission):
		return self.role.has_permission(permission)

	def is_administrator(self):
		return self.role.has_permission(Permission.ADMIN)

	
db.event.listen(User.about_me,"set",User.on_changed_about)

