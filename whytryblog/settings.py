# -*- coding: utf-8 -*-

import os
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

class BaseConfig(object):
	SECRET_KEY = os.getenv('SECRET_KEY')
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	MAIL_SERVER = os.getenv('MAIL_SERVER','smtp.qq.com')
	MAIL_PORT = os.getenv('MAIL_PORT','465')
	MAIL_USE_SSL = True
	MAIL_USE_TLS = True
	MAIL_USERNAME = os.getenv('MAIL_USERNAME','479260115@qq.com')
	MAIL_PASSWORD = os.getenv('SENDGRID_API_KEY','dtqoehgzpkuibgcg')
	MAIL_DEFAULT_SENDER=('WHY',os.getenv('MAIL_USERNAME'))

	WHYBLOG_GETMSG_EMAIL = os.getenv('WHYBLOG_GETMSG_EMAIL')
	WHYBLOG_ADMIN_EMAIL = os.getenv('WHYBLOG_ADMIN_EMAIL')
	
	WHYBLOG_POST_PER_PAGE = 10
	WHYBLOG_MANAGE_POST_PER_PAGE = 15
	WHYBLOG_COMMENT_PER_PAGE = 15
	WHYBLOG_SEARCH_RESULT_PER_PAGE = 15

	WHOOSHEE_MIN_STRING_LEN = 1

	SSL_DISABLE = True
	
	#WHOOSH_BASE = os.path.join(basedir, 'WHOOSH_BASE_INDEX')

	SQLALCHEMY_POOL_RECYCLE = 280

	

class DevelopmentConfig(BaseConfig):
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir,'data-dev.db')

class TestingConfig(BaseConfig):
	TESTING = True
	#测试时关闭csrf
	WTF_CSRF_ENABLED = False
	SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(BaseConfig):
	SSL_DISABLE = os.getenv('SSL_DISABLE','False')
	SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL','sqlite:///' + os.path.join(basedir,'data.db'))


config = {
	'development':DevelopmentConfig,
	'testing':TestingConfig,
	'production':ProductionConfig
}