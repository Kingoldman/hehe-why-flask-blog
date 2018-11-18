# -*- coding: utf-8 -*-

from flask import Blueprint,render_template,flash,url_for,current_app,request,redirect,session,make_response,abort
from flask import Blueprint
from flask_login import current_user,login_required
from whytryblog.models import Admin,Post,Category,Comment
from whytryblog.utils import redirect_back
from whytryblog.forms import PostForm,SettingForm,CategoryForm
from whytryblog.extensions import db

admin_bp = Blueprint('admin',__name__)


@admin_bp.route('/settings',methods = ['GET','POST'])
@login_required
def settings():
	form = SettingForm()
	if form.validate_on_submit():
		current_user.name = form.name.data
		current_user.blog_title = form.blog_title.data
		current_user.blog_sub_title = form.blog_sub_title.data
		current_user.about = form.about.data
		db.session.commit()
		flash("设置更新","success")
		return redirect(url_for('blog.index'))

	form.name.data = current_user.name
	form.blog_title.data = current_user.blog_title
	form.blog_sub_title.data = current_user.blog_sub_title
	form.about.data = current_user.about
	return render_template('admin/settings.html',form = form)


	
@admin_bp.route('/manage_post')
@login_required
def manage_post():
	page = request.args.get('page',1,type = int)
	pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page,per_page = current_app.config['WHYBLOG_MANAGE_POST_PER_PAGE'])
	posts = pagination.items
	
	return render_template('admin/manage_post.html',page = page,pagination = pagination,posts = posts)


@admin_bp.route('/new_post',methods = ['GET','POST'])
@login_required
def new_post():
	current_app.config['CKEDITOR_FILE_UPLOADER'] = 'upload'
	form = PostForm()
	if form.validate_on_submit():
		title = form.title.data
		category = Category.query.get(form.category.data)
		body = form.body.data
		post = Post(title = title,category = category,body = body)
		db.session.add(post)
		db.session.commit()
		flash("文章发表成功！","success")
		return redirect(url_for('blog.show_post',post_id = post.id))
	
	return render_template('admin/new_post.html',form = form)


@admin_bp.route('/edit_post/<int:post_id>',methods = ['GET','POST'])
@login_required
def edit_post(post_id):
	form = PostForm()
	post = Post.query.get_or_404(post_id)
	if form.validate_on_submit():
		post.title = form.title.data
		post.category = Category.query.get(form.category.data)
		post.body = form.body.data
		db.session.commit()
		flash("文章修改成功！","success")
		return redirect(url_for('blog.show_post',post_id = post.id))

	form.title.data = post.title
	#choice的值是ID
	form.category.data = post.category_id
	form.body.data = post.body
	
	return render_template('admin/edit_post.html',form = form)


@admin_bp.route('/delete_post/<int:post_id>',methods = ['POST'])
@login_required
def delete_post(post_id):
	post = Post.query.get_or_404(post_id)
	db.session.delete(post)
	db.session.commit()
	flash("文章已删除！","warning")
	return redirect_back()



#####comment
@admin_bp.route('/set_comment/<int:post_id>',methods = ['POST'])
@login_required
def set_comment(post_id):
	post = Post.query.get_or_404(post_id)
	if post.can_comment:
		post.can_comment = False
		flash('文章评论已禁用', 'warning')
	else:
		post.can_comment = True
		flash('文章评论已启用', 'success')
	db.session.commit()
	return redirect_back()


@admin_bp.route('/manage_comment')
@login_required
def manage_comment():
	filter_rule = request.args.get('filter','all')
	## 'all', 'unreviewed', 'admin'
	page = request.args.get('page',1,type = int)
	if filter_rule == 'unreviewed':
		filtered_comments = Comment.query.filter_by(reviewed = False)
	elif filter_rule == 'admin':
		filtered_comments = Comment.query.filter_by(from_admin = True)
	else:
		filtered_comments = Comment.query
	pagination = filtered_comments.order_by(Comment.timestamp.desc()).paginate(page,per_page = current_app.config['WHYBLOG_COMMENT_PER_PAGE'])
	comments = pagination.items

	return render_template('admin/manage_comment.html',pagination = pagination,comments = comments)


@admin_bp.route('/examine_comment/<int:comment_id>/', methods=['POST'])
@login_required
def examine_comment(comment_id):
	comment = Comment.query.get_or_404(comment_id)
	comment.reviewed = True
	db.session.commit()
	flash("评论审核通过","success")
	return redirect_back()

@admin_bp.route('/delete_comment/<int:comment_id>/', methods=['POST'])
@login_required
def delete_comment(comment_id):
	comment = Comment.query.get_or_404(comment_id)
	db.session.delete(comment)
	db.session.commit()
	flash("评论已删除","warning")
	return redirect_back()
#####comment


##category
@admin_bp.route('/manage_category')
@login_required
def manage_category():
	return render_template('admin/manage_category.html')


@admin_bp.route('/new_category', methods=['GET', 'POST'])
@login_required
def new_category():
	form = CategoryForm()
	if form.validate_on_submit():
		name = form.name.data
		category = Category(name = name )
		db.session.add(category)
		db.session.commit()
		flash("分类建立成功！",'success')
		return redirect(url_for('admin.manage_category'))
	return render_template('admin/new_category.html',form= form)


@admin_bp.route('/edit_category/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
	form = CategoryForm()
	category = Category.query.get_or_404(category_id)
	if category.id == 1:
		flash("默认分类不能编辑","danger")
		return redirect(url_for('blog.index'))
	if form.validate_on_submit():
		category.name = form.name.data
		db.session.commit()
		flash("分类编辑成功！",'success')
		return redirect(url_for('admin.manage_category'))
	form.name.data = category.name
	return render_template('admin/edit_category.html',form= form)


@admin_bp.route('/delete_category/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
	category = Category.query.get_or_404(category_id)
	if category.id == 1:
		flash("默认分类不能编辑","danger")
		return redirect(url_for('blog.index'))
	#自定义方法,删除分类下的文章变为默认分类
	category.delete()
	flash("分类已删除！")
	return redirect(url_for('admin.manage_category'))

##category