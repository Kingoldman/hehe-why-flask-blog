# -*- coding: utf-8 -*-
from flask import Flask,render_template,request
from whytryblog.settings import config
from whytryblog.extensions import bootstrap,db,mail,moment,ckeditor,login_manager,csrf,whooshee,migrate
from whytryblog.blueprints.admin import admin_bp
from whytryblog.blueprints.auth import auth_bp 
from whytryblog.blueprints.blog import blog_bp
from whytryblog.models import Admin,Category,Post,Comment
import os
import click
from flask_wtf.csrf import CSRFError
import logging
from logging.handlers import SMTPHandler,RotatingFileHandler

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

def create_app(config_name=None):
	if config_name == None:
		config_name = os.getenv('FLASK_CONFIG','development')

	app = Flask("whytryblog")
	app.config.from_object(config[config_name])

	#处理代理服务器首部
	#from werkzeug.contrib.fixers import ProxyFix
	#app.wsgi_app = ProxyFix(app.wsgi_app)

	from flask_sslify import SSLify
	sslify = SSLify(app)

	register_logging(app)
	register_extensions(app)
	register_blueprints(app)
	register_shell_context(app)
	register_template_context(app)
	register_errors(app)
	register_commands(app)
	migrate.init_app(app,db)

	return app


#日志
def register_logging(app):
	class RequestFormatter(logging.Formatter):
		def format(self,record):
			record.url = request.url
			record.remote_addr = request.remote_addr
			return super(RequestFormatter,self).format(record)

	request_formatter = RequestFormatter(
		'[%(asctime)s] %(remote_addr)s requested %(url)s\n'
        '%(levelname)s in %(module)s: %(message)s'
        )

	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

	file_handler = RotatingFileHandler(os.path.join(basedir, 'logs/whyblog.log'),maxBytes=10 * 1024 * 1024, backupCount=10)

	file_handler.setFormatter(formatter)
	file_handler.setLevel(logging.INFO)

	mail_handler = SMTPHandler(
		mailhost=app.config['MAIL_SERVER'],
		fromaddr=app.config['MAIL_USERNAME'],
		toaddrs=app.config['WHYBLOG_GETMSG_EMAIL'],
		subject='WHYblog Application Error',
		credentials=(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD']))

	mail_handler.setLevel(logging.ERROR)
	mail_handler.setFormatter(request_formatter)

	if not app.debug:
		app.logger.addHandler(mail_handler)
		app.logger.addHandler(file_handler)





#扩展
def register_extensions(app):
	bootstrap.init_app(app)
	db.init_app(app)
	moment.init_app(app)
	ckeditor.init_app(app)
	mail.init_app(app)
	login_manager.init_app(app)
	csrf.init_app(app)
	whooshee.init_app(app)
	



#蓝本
def register_blueprints(app):
	app.register_blueprint(blog_bp)
	app.register_blueprint(auth_bp,url_prefix = '/auth')
	app.register_blueprint(admin_bp,url_prefix = '/admin')

#上下文
def register_shell_context(app):
	@app.shell_context_processor
	def make_shell_context():
		return dict(db = db,Admin =Admin,Category = Category,Post = Post,Comment = Comment)

def register_template_context(app):
	@app.context_processor
	def make_template_context():
		admin = Admin.query.first()
		categories = Category.query.order_by(Category.name).all() 
		return dict(admin = admin,categories = categories)

#错误
def register_errors(app):
	@app.errorhandler(400)
	def bad_request(e):
		return render_template('errors/400.html'),400

	@app.errorhandler(404)
	def page_not_found(e):
		return render_template('errors/404.html'),404

	@app.errorhandler(500)
	def internal_server_error(e):
		return render_template('errors/500.html'),500

	@app.errorhandler(CSRFError)
	def handle_csrf_error(e):
		return render_template('errors/400.html',description = e.description),400



def register_commands(app):

	@app.cli.command()
	@click.option('--drop',is_flag=True,help='create after drop')
	def initdb(drop):
		if drop:
			click.confirm('delete db?',abort=True)
			db.drop_all()
			click.echo('drop db')
		db.create_all()
		click.echo('initdb')


	@app.cli.command()
	@click.option('--username', prompt=True, help='The username used to login.')
	@click.option('--password', prompt=True, hide_input=True,confirmation_prompt=True, help='The password used to login.')

	#部署之后建立账号
	def init(username, password):
		click.echo('Initializing the database...')
		db.create_all()

		admin = Admin.query.first()
		if admin is not None:
			click.echo('The administrator already exists, updating...')
			admin.username = username
			admin.set_password(password)
		else:
			click.echo('Creating the temporary administrator account...')
			admin = Admin(
				username=username,
				blog_title='邻家王叔叔',
				blog_sub_title="宇宙十佳中年",
				name='Admin',
				about='呵呵。'
				)
			admin.set_password(password)
			db.session.add(admin)

		category = Category.query.first()
		if category is None:
			click.echo('Creating the default category...')
			category = Category(name='Default')
			db.session.add(category)

		db.session.commit()
		click.echo('Done.')


	@app.cli.command()
	@click.option('--category',default=10,help='category')
	@click.option('--post',default=50,help='post')
	@click.option('--comment',default=500,help='comment')
	def forge(category,post,comment):
		from whytryblog.fakes import fake_admin,fake_posts,fake_categories,fake_comments
		
		db.drop_all()
		db.create_all()

		click.echo('fake_admin')
		fake_admin()

		click.echo('fake_categories')
		fake_categories()

		click.echo('fake_posts')
		fake_posts()

		click.echo('fake_comments')
		fake_comments()

		click.echo('done')


