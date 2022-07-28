from flask_wtf import FlaskForm
from flask_pagedown.fields import PageDownField
from wtforms import StringField,SubmitField,SelectField,ValidationError,TextAreaField
from wtforms.validators import DataRequired,Optional,Regexp,Email
from ..models import Role


class EditProfileForm(FlaskForm):
	name = StringField("Name",validators=[Optional()])
	location = StringField("Location",validators=[Optional()])
	gender   = StringField("Gender")
	about_me = PageDownField("About me")
	submit   = SubmitField("Update")



	def validate_gender(self,field):
		if field.data.lower() not in ["other","male","female"]:
			raise ValidationError("Please Specify your gender correctly")


class CommentEditForm(FlaskForm):
	body = TextAreaField("Edit your comment",validators=[DataRequired()])
	submit = SubmitField("Update")

class ReplyForm(FlaskForm):
		body = TextAreaField("reply",validators=[DataRequired()])
		submit=SubmitField("reply")

class CommentForm(FlaskForm):
	comment = TextAreaField("Type Your Comment Here",validators=[DataRequired()])
	submit  = SubmitField("Comment")
	
class AdminProfileForm(FlaskForm):
	name = StringField("Name",validators=[DataRequired()])
	username = StringField("Username",validators=[DataRequired(),Regexp("^[a-zA-Z][a-zA-Z0-9]*$",0,"username must start with letters ")])
	role = SelectField("Role",coerce=int,validators=[DataRequired()])
	email = StringField("Email",validators=[DataRequired(),Email()])
	location = StringField("Location",validators=[DataRequired()])
	about_me = TextAreaField("About me",validators=[DataRequired()])
	gender  = StringField("Gender",validators=[DataRequired()])
	submit = SubmitField("Update")

	def __init__(self,**kargs):
		super(AdminProfileForm,self).__init__(**kargs)
		self.role.choices =[(role.id,role.name) for role in Role.query.all()] 

class PostForm(FlaskForm):
	title  = StringField(validators=[DataRequired()])
	content = PageDownField(validators=[DataRequired()])
	submit  = SubmitField("Post")
