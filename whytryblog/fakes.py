# -*- coding: utf-8 -*-

from whytryblog.models import Admin,Category,Post,Comment
from whytryblog.extensions import db
from faker import Faker
import random

fake = Faker()

def fake_admin():
	admin = Admin(username = 'admin',blog_title = 'whytryblog',blog_sub_title = '宇宙十佳青年王老汉',name = 'why',about = 'qqqqqqqqqqqqqq')
	admin.set_password('123')
	db.session.add(admin)
	db.session.commit()

def fake_categories(count = 10):
	#先建立一个不能更改的默认分类
	category = Category(name = 'default')
	db.session.add(category)

	for i in range(count):
		category = Category(name = fake.word())
		db.session.add(category)
		try:
			db.session.commit()
		except:
			db.session.rollback()

def fake_posts(count = 50):
	for i in range(count):
		post = Post(title = fake.sentence(),body = fake.text(2000),category = Category.query.get(random.randint(1,Category.query.count())),timestamp = fake.date_time_this_year())
		db.session.add(post)
	db.session.commit()


def fake_comments(count = 100):
	for i in range(count):
		#审核过的
		comment = Comment(
			author = fake.name(),
			email = fake.email(),
			body = fake.sentence(),
			timestamp = fake.date_time_this_year(),
			reviewed = True,
			post = Post.query.get(random.randint(1,Post.query.count()))
			)
		db.session.add(comment)

	salt = int(count*0.1)
	for i in range(salt):
		#未审核评论
		comment = Comment(
			author = fake.name(),
			email = fake.email(),
			body = fake.sentence(),
			timestamp = fake.date_time_this_year(),
			reviewed = False,
			post = Post.query.get(random.randint(1,Post.query.count()))
			)
		db.session.add(comment)

		#管理员发表
		comment = Comment(
			author = 'why',
			email = 'www@qq.com',
			body = fake.sentence(),
			timestamp = fake.date_time_this_year(),
			reviewed = True,
			from_admin = True,
			post = Post.query.get(random.randint(1,Post.query.count()))
			)
		db.session.add(comment)
	db.session.commit()

	#回复
	for i in range(salt):
		comment = Comment(
			author = fake.name(),
			email = fake.email(),
			body = fake.sentence(),
			timestamp = fake.date_time_this_year(),
			reviewed = True,
			post = Post.query.get(random.randint(1,Post.query.count()))
			)
		db.session.add(comment)
	db.session.commit()

