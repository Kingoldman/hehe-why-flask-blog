# -*- coding: utf-8 -*-
from whytryblog.extensions import mail
from flask_mail import Message
from threading import Thread
from flask import current_app,render_template,url_for


def send_async_email(app,msg):
	with app.app_context():
		mail.send(msg)



def send_new_comment_email(post):
	app = current_app._get_current_object()
	post_url = url_for('blog.show_post', post_id=post.id, _external=True) + '#comments'
	to = current_app.config['WHYBLOG_GETMSG_EMAIL']
	message = Message(subject = "New comment", sender = current_app.config['WHYBLOG_GETMSG_EMAIL'],recipients=[to])
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
	message = Message(subject = "New Reply", sender = current_app.config['WHYBLOG_GETMSG_EMAIL'],recipients=[to])
	message.html = render_template('blog/new_reply_email.html',comment = comment,post_url = post_url)
	thr = Thread(target=send_async_email, args=[app, message])
	thr.start()
	return thr

