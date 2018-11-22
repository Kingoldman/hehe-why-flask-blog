# -*- coding: utf-8 -*-
from whytryblog.extensions import mail
from flask_mail import Message
from threading import Thread
from flask import current_app,render_template,url_for
import os,sendgrid
from sendgrid.helpers.mail import *


def send_async_email(app,msg):
	with app.app_context():
		mail.send(msg)


#flask-mail
def send_new_comment_email(post):
	app = current_app._get_current_object()
	post_url = url_for('blog.show_post', post_id=post.id, _external=True) + '#comments'
	to = current_app.config['WHYBLOG_GETMSG_EMAIL']
	message = Message(subject = "New comment",recipients=[to])
	message.html = render_template('blog/new_comment_email.html',post = post,post_url = post_url)
	thr = Thread(target=send_async_email, args=[app, message])
	thr.start()
	return thr


def send_new_reply_email(comment):
	app = current_app._get_current_object()
	post_url = url_for('blog.show_post', post_id=comment.post_id, _external=True) + '#comments'
	if comment.from_admin:
		to = current_app.config['WHYBLOG_GETMSG_EMAIL']
	else:
		to = comment.email
	message = Message(subject = "New Reply",recipients=[to])
	message.html = render_template('blog/new_reply_email.html',comment = comment,post_url = post_url)
	thr = Thread(target=send_async_email, args=[app, message])
	thr.start()
	return thr



#sendgrid
def send_mail_by_api(subject,to,body):
	sg = sendgrid.SendGridAPIClient(apikey = os.environ.get('SENDGRID_API_KEY'))
	from_email =Email('why@unclewhy.pythonanywhere.com')
	to_email = Email(to)
	content = Content("text/html",body)
	mail = Mail(from_email,subject,to_email,content)
	response = sg.client.mail.send.post(request_body = mail.get())

def send_new_comment_email_by_api(post):
	post_url = url_for('blog.show_post', post_id=post.id, _external=True) + '#comments'
	to = current_app.config['WHYBLOG_GETMSG_EMAIL']
	subject = "New comment"
	body =  render_template('blog/new_comment_email.html',post = post,post_url = post_url)
	send_mail_by_api(subject = subject,to = to ,body = body)

def send_new_reply_email_by_api(comment):
	
	post_url = url_for('blog.show_post', post_id=comment.post_id, _external=True) + '#comments'
	if comment.from_admin:
		to = current_app.config['WHYBLOG_GETMSG_EMAIL']
	else:
		to = comment.email
	subject = "New Reply"
	body = render_template('blog/new_reply_email.html',comment = comment,post_url = post_url)
	send_mail_by_api(subject = subject,to = to ,body = body)