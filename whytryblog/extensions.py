# -*- coding: utf-8 -*-

#扩展
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_ckeditor import CKEditor
from flask_moment import Moment
from flask_login import LoginManager
from flask_wtf import CSRFProtect
#from flask_whooshee import Whooshee
from flask_migrate import Migrate


bootstrap = Bootstrap()
db = SQLAlchemy()
mail = Mail()
moment = Moment()
ckeditor = CKEditor()
login_manager = LoginManager()
csrf = CSRFProtect()
#whooshee = Whooshee()
migrate = Migrate()


@login_manager.user_loader
def load_user(user_id):
	from whytryblog.models import Admin
	user = Admin.query.get(int(user_id))
	return user


#login_required
login_manager.login_view = 'auth.login'