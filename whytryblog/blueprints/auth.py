# -*- coding: utf-8 -*-

#认证蓝本
from flask import Blueprint,render_template,flash,url_for,redirect,flash
from flask_login import login_user,logout_user,current_user,login_required
from whytryblog.models import Admin
from whytryblog.forms import LoginForm
from whytryblog.utils import redirect_back,generate_verification_code


auth_bp = Blueprint('auth',__name__)



@auth_bp.route('/login',methods = ['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('blog.index'))

	form = LoginForm()
	if form.validate_on_submit():
		username = form.username.data
		password = form.password.data
		remember_me = form.remember_me.data
		admin = Admin.query.first()
		if admin:
			if username == admin.username and admin.validate_password(password):
				login_user(admin,remember_me)
				flash("登陆成功！","success")
				return redirect_back()
			else:
				flash("账号或密码错误！","danger")
		else:
			flash("无此账号！","warning")

	return render_template('auth/login.html',form = form)



@auth_bp.route('/logout')
@login_required
def logout():
	logout_user()
	flash("账号退出！","success")
	return redirect_back()


