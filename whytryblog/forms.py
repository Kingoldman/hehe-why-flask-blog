# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField,BooleanField,SelectField,TextAreaField,HiddenField
from wtforms.validators import DataRequired,Length,Email,EqualTo,ValidationError
from flask_ckeditor import CKEditorField
from whytryblog.models import Category



#登陆
class LoginForm(FlaskForm):
	#email = StringField('Email',validators = [DataRequired(),Email(message="邮箱格式错误")],render_kw={"placeholder": "yourname@example.com"})
	username = StringField('用户名',validators=[DataRequired()],render_kw={"placeholder": "请输入用户名"})
	password = PasswordField('密码',validators=[DataRequired()],render_kw={"placeholder": "请输入密码"})
	remember_me = BooleanField('记住我')
	submit = SubmitField('登陆')


#文章
class PostForm(FlaskForm):
	title = StringField('标题',validators = [DataRequired(),Length(1,60)])
	category = SelectField('分类',coerce = int,default =1)
	body = CKEditorField('内容',validators = [DataRequired()] )
	submit = SubmitField("发表")

	def __init__(self,*args,**kwargs):
		super(PostForm,self).__init__(*args,**kwargs)
		self.category.choices = [(category.id,category.name) for category in Category.query.order_by(Category.name).all() ]

#分类
class CategoryForm(FlaskForm):
	name = StringField('类别名称',validators = [DataRequired(),Length(1,30)],render_kw={"placeholder": "请输入类别名称"})
	submit = SubmitField("确定")

	def validate_name(self,field):
		if Category.query.filter_by(name = field.data).first():
			raise ValidationError('分类已存在')

#评论
class CommentForm(FlaskForm):
	author = StringField('Name',validators = [DataRequired(),Length(1,30)],render_kw={"placeholder": "your name"})
	email = StringField('Email',validators = [DataRequired(),Email(message="邮箱格式错误"),Length(1,254)],render_kw={"placeholder": "yourname@example.com"})
	body = TextAreaField('Content',validators = [DataRequired()],render_kw={"placeholder": "评论内容"})
	verification_code = StringField('验证码',validators = [DataRequired()],render_kw={"placeholder": "请输入验证码"})
	submit = SubmitField("提交评论")

#管理员评论
class AdminCommentForm(CommentForm):
	author = HiddenField()
	email = HiddenField()



class SettingForm(FlaskForm):
	name = StringField('Name',validators = [DataRequired(),Length(1,60)])
	blog_title = StringField('Blog Title',validators = [DataRequired(),Length(1,60)])
	blog_sub_title = StringField('Blog Sub Title',validators = [DataRequired(),Length(1,100)])
	about = TextAreaField('About',validators = [DataRequired()])
	submit = SubmitField('确定')
