from .. import db
from flask import render_template,url_for,request,flash,session,redirect
from .forms import LoginForm,RegisterForm,UsernameForm,PasswordResetForm
from . import auth
from ..models import User
from flask_login import login_user,current_user,login_required,logout_user
from ..email import send_mail



@auth.route("/login",methods=["GET","POST"])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user != None and user.verify_password(form.password.data):
				login_user(user,form.remember.data)
				next = request.args.get("next")
				if next == None or not next.startswith("/"):
					next = url_for("main.index")
				return  redirect(next)
		flash("invalid password or email address")
	return render_template("sign-in/login.html",form=form)



@auth.route("/register",methods=["POST","GET"])
def register():
	gender = ["Female","Male","Others"]
	form = RegisterForm()
	if current_user.is_authenticated:
		logout_user()

	if form.validate_on_submit():
		user = User(username=form.username.data,password=form.password.data,\
		email = form.email.data,gender=gender[form.gender.data])
		db.session.add(user)
		db.session.commit()
		login_user(user,form.remember.data)
		token = user.generate_confirmation_token()
		send_mail(form.email.data,"confirmation","mail/confirmation",user=user,token=token)
		return redirect(url_for("auth.unconfirm"))
		flash("confirmation mail has been sent to you please check your mailbox")
	return render_template("sign-up/register.html",form=form)

@auth.route("/confirm",methods=["POST","GET"])
def confirm():
	form = UsernameForm()
	if form.validate_on_submit():
		session["username"] = form.username.data
		url = url_for("auth.reset")
		return redirect(url)
		flash("Type New Password")
	return render_template("sign-in/user_confirm.html",form=form)

@auth.route("/reset",methods=["POST","GET"])
def reset():	
	user = session.get("username")
	if not user:
		return redirect(url_for("auth.confirm"))
	form = PasswordResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=user).first()
		token = user.generate_pass_reset_token(password=form.password.data)
		send_mail(user.email,"Password Reset","mail/password_change",token=token,user=current_user)
		flash("check your mail box we have sent you the verification link")
		return redirect(url_for("auth.login"))
	return render_template("sign-in/reset_password.html",form=form)

@auth.route("/confirm_password/<token>")
def confirm_reset_password(token):
	u = User.confirm_user(token)
	if u:
		flash("you have successfully changed your password")
		flash("log using your new password")
		db.session.commit()
		return redirect(url_for("auth.login"))
	flash("token is expired try again")
	return redirect(url_for("auth.reset"))


@auth.route("/resend_confirmation")
@login_required
def resend_confirmation_token():
	user = current_user._get_current_object()
	token = user.generate_confirmation_token()
	send_mail(user.email,"confirmation","mail/confirmation",token=token,user=user)
	flash("confirmation mail has been sent to you")
	return redirect(url_for("auth.unconfirm"))


@auth.route("/unconfirm")
@login_required
def unconfirm():
	return render_template("sign-in/unconfirmed.html",user=current_user)


@auth.route("/confirm/<token>")
def confirm_register(token):
	confirmed = current_user.confirm(token)
	if confirmed:
		flash("successfully confirmed")
		return redirect(url_for("auth.login"))
	flash("confirmation link invalid or expired")
	return redirect(url_for("auth.unconfirm"))


@auth.route("/logout")
def logout():
	logout_user()
	return redirect(url_for("main.index"))
