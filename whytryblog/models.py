# -*- coding: utf-8 -*-
from datetime import datetime
from whytryblog.extensions import db,whooshee
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin

class Admin(db.Model,UserMixin):
	id = db.Column(db.Integer,primary_key = True)
	username = db.Column(db.String(20))
	password_hash = db.Column(db.String(128))
	blog_title = db.Column(db.String(60))
	blog_sub_title = db.Column(db.String(100))
	name = db.Column(db.String(30))
	about = db.Column(db.Text)

	@property
	def password(self):
		raise AttributeError("NOT READ")

	def set_password(self,password):
		self.password_hash = generate_password_hash(password)

	def validate_password(self,password):
		return check_password_hash(self.password_hash,password)


class Category(db.Model):
	id = db.Column(db.Integer,primary_key = True)
	name = db.Column(db.String(30),unique = True)

	posts = db.relationship('Post',back_populates = 'category')

	#删除分类改默认分类
	def delete(self):
		default_category = Category.query.get(1)
		posts = self.posts[:]
		for post in posts:
			post.category = default_category
		db.session.delete(self)
		db.session.commit()

	def __repr__(self):
		return self.name


@whooshee.register_model('title','body')
class Post(db.Model):

	id = db.Column(db.Integer,primary_key = True)
	title = db.Column(db.String(60))
	body = db.Column(db.Text)
	timestamp = db.Column(db.DateTime,default = datetime.utcnow,index = True)
	can_comment = db.Column(db.Boolean,default = True)

	category_id = db.Column(db.Integer,db.ForeignKey('category.id'))
	category = db.relationship('Category',back_populates = 'posts')

	comments = db.relationship('Comment',back_populates = 'post',cascade='all,delete-orphan')

	def get_all_reviewed_comments(self):
		return [comment for comment in self.comments if comment.reviewed]


@whooshee.register_model('author','body')
class Comment(db.Model):

	id = db.Column(db.Integer,primary_key = True)
	author = db.Column(db.String(30))
	email = db.Column(db.String(254))
	body = db.Column(db.Text)
	from_admin = db.Column(db.Boolean,default = False)
	reviewed = db.Column(db.Boolean,default = False)
	timestamp = db.Column(db.DateTime,default = datetime.utcnow,index = True)

	post_id = db.Column(db.Integer,db.ForeignKey('post.id'))
	post = db.relationship('Post',back_populates = 'comments')

	#评论的评论
	replied_id = db.Column(db.Integer,db.ForeignKey('comment.id'))
	replied = db.relationship('Comment',back_populates = 'replies',remote_side = [id])
	
	replies = db.relationship('Comment',back_populates = 'replied',cascade = 'all,delete-orphan')


