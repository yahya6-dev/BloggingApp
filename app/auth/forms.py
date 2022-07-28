from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,BooleanField,ValidationError,SelectField
from wtforms.validators import DataRequired,Length,Email,Optional,Regexp,EqualTo
from ..models import User

class LoginForm(FlaskForm):
	email = StringField(validators=[DataRequired(),Email()])
	password = PasswordField(validators=[DataRequired()])
	remember = BooleanField(validators=[Optional()])
	submit = SubmitField()

class RegisterForm(FlaskForm):
	username = StringField(validators=[DataRequired(),Regexp("^[a-zA-Z][a-zA-Z0-9_]*$",0,"Username must begin with letter,number or underscore")])
	password = PasswordField(validators=[DataRequired(),Length(6,64)])
	confirm  = PasswordField(validators=[DataRequired(),EqualTo("password",message="password didnt match")])
	email    = StringField(validators=[DataRequired(),Email()])
	gender   = SelectField("Choose Gender",coerce=int,validators=[DataRequired()])
	submit   = SubmitField()
	remember = BooleanField(validators=[Optional()])

	def __init__(self,**kargs):
		super(RegisterForm,self).__init__(**kargs)
		self.gender.choices = [(sn,label) for sn,label in enumerate(["Female","Male","Others"])]


	def validate_username(self,field):
		if User.query.filter_by(username=field.data).first() != None:
			raise ValidationError("Username is already taken")

	def validate_email(self,field):
		if User.query.filter_by(email=field.data).first() != None:
			raise ValidationError("Email already registered")


class UsernameForm(FlaskForm):
	username = StringField(validators=[DataRequired()])
	submit   = SubmitField()

	def validate_username(self,field):
		if not User.query.filter_by(username=field.data).first():
			raise ValidationError("No Such User %s"%field.data)

class PasswordResetForm(FlaskForm):

	password = PasswordField(validators=[DataRequired()])
	confirm = PasswordField(validators=[DataRequired()])
	submit    = SubmitField()


