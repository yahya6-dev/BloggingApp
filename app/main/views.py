from flask import render_template,request,flash,abort,redirect,url_for,current_app,session
from . import main
from flask_login import  login_required,current_user
from ..models import User,Post
from .forms import EditProfileForm,PostForm
from .. import db
from ..models import Post,User,Role,Comment,Reply
from ..decorators import admin_required,permission_required
from . forms import AdminProfileForm,CommentForm,CommentEditForm,ReplyForm 
from ..models import Permission


@main.route("/",methods=["POST","GET"])
def index():
	long_post = Post.query.filter_by(long_post=True).first()
	first  = Post.query.order_by(Post.timestamp.desc()).first()
	second = Post.query.order_by(Post.timestamp.desc()).offset(4)[-1]


	page = request.args.get("page",1,type=int)
	pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page,per_page=current_app.config.get("BLOGGING_POST_PER_PAGE") or 10,error_out=True)
	posts = pagination.items
	return render_template("main/index.html",second=second,long_post=long_post,first=first,page=page,posts=posts,pagination=pagination)


@main.route("/edit_comment/<id>",methods=["POST","GET"])
@login_required
def edit_comment(id):
	form = CommentEditForm()
	comment = Comment.query.get_or_404(id)
	if current_user.username != comment.author.username:
		abort(404)
	post    = comment.post
	if form.validate_on_submit():
		comment.comment_body = form.body.data
		db.session.add(comment)
		db.session.commit()
		url = url_for(".comments",id=post.id)
		flash("successfully updated")
		return redirect(url)
	else:
		form.body.data = comment.comment_body
		return render_template("main/edit.html",form=form,comment=comment)


@main.route("/disabled_post/<id>")
@permission_required(Permission.MODERATE)
def disable_post(id):
	post = Post.query.get_or_404(id)
	post.disabled = not post.disabled 
	db.session.add(post)
	db.session.commit()
	page = request.args.get("page",type=int)
	return redirect(url_for("main.index",page=page))

@main.route("/delete_post/<id>")
@permission_required(Permission.MODERATE)
def delete_post(id):
	post = Post.query.get_or_404(id)
	db.session.delete(post)
	db.session.commit()

@main.route("/like/<id>")
@login_required
def like(id):
	u =  current_user._get_current_object()
	post = Post.query.get_or_404(id)
	if post.disabled:
		abort(404)
	if post.is_liking(u):
		post.unlike(u)
	else:
		post.add_like(u)

	db.session.commit()
	page = request.args.get("page",1,type=int)
	return redirect(url_for("main.index",page=page)+"#"+str(post.id))
	


@main.route("/like_prof/<id>")
@login_required
def like_prof(id):
	u =  current_user._get_current_object()
	post = Post.query.get_or_404(id)
	if post.disabled:
		abort(404)
	if post.is_liking(u):
		post.unlike(u)
	else:
		post.add_like(u)

	db.session.commit()
	url  = url_for(".user",username=post.author.username)+"#"+str(post.id)  
	return redirect(url)
	
@main.route("/user/<username>",methods=["GET","POST"])
@login_required
def user(username):
	form = PostForm()
	if form.validate_on_submit():
		post = Post(post_body=form.content.data,author=current_user._get_current_object(),title=form.title.data)
		if len(post.post_body) >= 320:
			post.long_post = True
		db.session.add(post)
		db.session.commit()
		form.title.data = ''
		form.content.data = ''
		flash("post successfully")
		return redirect(url_for("main.user",username=username))

	user = User.query.filter_by(username=username).first_or_404()
	posts  = user.posts.order_by(Post.timestamp.desc()).all()
	return render_template("main/profile.html", user=user,posts=posts,form=form)


@main.before_app_request
def before_request():
	if current_user.is_authenticated:
		current_user.ping()

@main.route("/edit/<user>",methods=["POST","GET"])
@login_required
def edit(user):
	user = User.query.filter_by(username=user).first()
	if user and user.username == current_user.username:

		user = current_user._get_current_object()
		form = EditProfileForm()
		if form.validate_on_submit():
			user.name = form.name.data
			user.location = form.location.data
			user.about_me = form.about_me.data
			user.gender   = form.gender.data
			db.session.add(user)
			db.session.commit()
			flash("successfully updated")
			return redirect(url_for(".user",username=user.username))

		form.location.data = user.location
		form.gender.data   = user.gender
		form.name.data     = user.name
		form.about_me.data = user.about_me
		return render_template("main/edit_profile.html",form=form)

	else:
		return abort(404)


@main.route("/admin_edit/<user>",methods=["POST","GET"])
@admin_required
def edit_user(user):
	user = User.query.filter_by(username=user).first_or_404()
	if user:
		form = AdminProfileForm()
		if form.validate_on_submit():
			user.name = form.name.data
			user.email = form.email.data
			user.gender = form.gender.data 
			user.username= form.username.data
			user.location = form.location.data
			user.about_me = form.about_me.data
			user.role = Role.query.get(form.role.data)
			db.session.add(user)
			db.session.commit()
			return redirect(url_for(".user",username=user.username))
		else:
			form.name.data = user.name
			form.username.data = user.username
			form.email.data = user.email
			form.gender.data = user.gender or "None"
			form.location = user.location
			form.role.data = user.role.id
			form.about_me.data = user.about_me
		return render_template("main/admin_edit.html",form=form)



@main.route("/follow/<user>")
@login_required
def follow(user):
	u = User.query.filter_by(username=user).first()
	follower = current_user._get_current_object()
	if not current_user.is_following(u):
		follower.follow(u)
		db.session.commit()
		flash("you are now following this user")
		return redirect(url_for("main.user",username=user))
	else:
		follower.unfollow(u)
		db.session.commit()
		flash("you are no longer following this user")
		return redirect(url_for("main.user",username=user))

@main.route("/followers/<user>")
@login_required
def followers(user):
	u  = User.query.filter_by(username=user).first_or_404()
	page = request.args.get("page",1,type=int)
	paginations = u.get_followers().paginate(page,per_page=30,error_out=True)
	followers = paginations.items
	return render_template("main/followers.html",followers=followers,page=page,user=u,paginations=paginations)





@main.route("/comment/<int:id>",methods=["POST","GET"])
@login_required
def comments(id):
	form = CommentForm()
	post = Post.query.get_or_404(id)
	if post.disabled:
		abort(404)
	if form.validate_on_submit():
		comment = Comment(comment_body=form.comment.data,post=post,author=current_user._get_current_object())
		db.session.add(comment)
		db.session.commit()
		url = url_for(".comments",id=id)+"#"+str(comment.id)
		return redirect(url)	

	page = request.args.get("page",1,type=int)
	pagination = post.comment_id.order_by(Comment.timestamp.desc()).paginate(page,per_page=30,error_out=True)
	comments = pagination.items
	return render_template("main/post.html",post=post,pagination=pagination,comments=comments,form=form)



@main.route("/delete_comment/<int:id>")
@login_required
def delete_comment(id):
	comment = Comment.query.get_or_404(id)
	post    = comment.post
	if  comment.author.username != current_user.username or not current_user.can(Permission.MODERATE):
		abort(404)
	db.session.delete(comment)
	db.session.commit()
	url = url_for(".comments",id=post.id)
	flash("successfully deleted")
	return redirect(url)



@main.route("/disable_comment/<int:id>")
@permission_required(Permission.MODERATE)
def disable_comment(id):
	comment = Comment.query.get_or_404(id)
	if  comment.author.username != current_user.username or not current_user.can(Permission.MODERATE):
		abort(404)
	comment.disabled = not comment.disabled
	db.session.add(comment)
	db.session.commit()
	url=url_for(".comments",id=comment.post.id)+"#"+str(comment.id)
	return redirect(url)


@main.route("/reply/<int:id>",methods=["POST","GET"])
def reply(id):
	comment = Comment.query.get_or_404(id)
	form = ReplyForm()
	if form.validate_on_submit():
		reply = Reply(user=current_user._get_current_object(),comment=comment,reply=form.body.data)
		db.session.add(reply)
		db.session.commit()
		return redirect(url_for(".comments",id=comment.post.id))
	return render_template("main/reply.html",form=form,comment=comment)

@main.route("/disabled_reply/<id>")
@login_required
def disabled_reply(id):
	reply = Reply.query.get_or_404(id)
	reply.disabled = not reply.disabled
	db.session.add(reply)
	db.session.commit()
