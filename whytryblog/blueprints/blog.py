# -*- coding: utf-8 -*-
from flask import Blueprint,render_template,flash,url_for,current_app,request,redirect,session,make_response,abort
from whytryblog.models import Admin,Post,Category,Comment
from whytryblog.forms import CommentForm,AdminCommentForm
from whytryblog.extensions import db
from whytryblog.utils import redirect_back,generate_verification_code
from flask_login import current_user
from whytryblog.emails import send_new_comment_email,send_new_reply_email,send_new_comment_email_by_api,send_new_reply_email_by_api

blog_bp = Blueprint('blog',__name__)


#验证码
@blog_bp.route('/verifycode',methods = ['POST','GET'])
def get_verify_code():
	#把strs发给前端,或者在后台使用session保存
    code_img, code_text = generate_verification_code()
    session['code_text'] = code_text
    response = make_response(code_img)
    response.headers['Content-Type'] = 'image/jpeg'
    return response

@blog_bp.route('/')
@blog_bp.route('/index')
def index():
	#当前页，默认为1
	page = request.args.get('page',1,type = int)
	#分页对象
	pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page,per_page = current_app.config['WHYBLOG_POST_PER_PAGE'] )
	posts = pagination.items
	return render_template('blog/index.html',pagination = pagination,posts = posts)


@blog_bp.route('/about')
def about():
	return render_template('blog/about.html')

@blog_bp.route('/category/<int:category_id>')
def by_category(category_id):
	page = request.args.get('page',1,type = int)
	category = Category.query.get_or_404(category_id)

	#with_parent()返回查询对象
	pagination = Post.query.with_parent(category).order_by(Post.timestamp.desc()).paginate(page,per_page = current_app.config['WHYBLOG_POST_PER_PAGE'] )
	posts = pagination.items
	return render_template('blog/category.html',category = category,pagination = pagination,posts = posts)


@blog_bp.route('/post/<int:post_id>',methods = ['GET','POST'])
def show_post(post_id):
	post = Post.query.get_or_404(post_id)
	page = request.args.get('page',1,type = int)

	#审核通过的评论
	pagination = Comment.query.with_parent(post).filter_by(reviewed = True).order_by(Comment.timestamp.desc()).paginate(page,per_page = current_app.config['WHYBLOG_COMMENT_PER_PAGE'] )
	comments = pagination.items

	if current_user.is_authenticated:
		form = AdminCommentForm()
		form.author.data = current_user.name
		form.email.data = current_app.config['WHYBLOG_ADMIN_EMAIL']
		from_admin = True
		reviewed = True
	else:
		form = CommentForm()
		from_admin = False
		reviewed = False

	if form.validate_on_submit():
		author = form.author.data
		email = form.email.data
		body = form.body.data
		if 'code_text' in session and session['code_text'].lower() != form.verification_code.data.lower():
			flash('验证码输入错误!',"warning")
		else:
			comment = Comment(author = author,email = email,body = body,post = post,reviewed = reviewed,from_admin = from_admin)
			#是否是回复评论，找到原评论再回复
			replied_id = request.args.get('reply')
			if replied_id:
				replied_comment = Comment.query.get_or_404(replied_id)
				comment.replied = replied_comment
				#send_new_reply_email(replied_comment)
				send_new_reply_email_by_api(replied_comment)
			db.session.add(comment)
			db.session.commit()


			if current_user.is_authenticated:
				flash("评论成功","success")
			else:
				#send_new_comment_email(post)
				send_new_comment_email_by_api(post)
				flash("评论已提交审核","info")

			return redirect(url_for('blog.show_post',post_id = post.id))

	return render_template('blog/post.html',post = post,pagination = pagination,comments = comments,form = form)


@blog_bp.route('/reply/comment/<int:comment_id>')
def reply_comment(comment_id):
	comment = Comment.query.get_or_404(comment_id)
	#url_for()多余的参数会自动转换为查询字符串，/post/11/?reply=4&author=ww#comment-form
	return redirect( url_for('blog.show_post',post_id = comment.post_id,reply = comment_id,author = comment.author) + '#comments')

@blog_bp.route('/search')
def search():
	whysearch = request.args.get('whysearch','')
	if whysearch == '':
		flash("请输入搜索内容！","warning")
		return redirect_back()
	#搜索类别
	search_category = request.args.get('search_category','post')
	page = request.args.get('page',1,type = int)

	all_search_posts_items = Post.query.whooshee_search(whysearch)
	all_search_comments_items = Comment.query.whooshee_search(whysearch).filter_by(reviewed = True)

	if search_category == 'post':
		#flask-whooshee覆盖了sqlalchemy的query对象，为其添加了whooshee_search()
		pagination = all_search_posts_items.paginate(page,per_page = current_app.config['WHYBLOG_SEARCH_RESULT_PER_PAGE'])
	else:	
		#sh_c == comment
		pagination = all_search_comments_items.paginate(page,per_page = current_app.config['WHYBLOG_SEARCH_RESULT_PER_PAGE'])

	results = pagination.items
	return render_template('blog/search_results.html',whysearch = whysearch,results = results,pagination = pagination,search_category = search_category,all_search_posts_items= all_search_posts_items.all(),all_search_comments_items = all_search_comments_items.all())

