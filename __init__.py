import os
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

db=SQLAlchemy(); login_manager=LoginManager(); csrf=CSRFProtect(); limiter=Limiter(key_func=get_remote_address,default_limits=['300 per hour'])

def create_app():
    load_dotenv(); app=Flask(__name__)
    uri=os.getenv('DATABASE_URL','sqlite:///yemeni_network.db').replace('postgres://','postgresql://',1)
    app.config.update(SECRET_KEY=os.getenv('SECRET_KEY','change-this-in-production'),SQLALCHEMY_DATABASE_URI=uri,SQLALCHEMY_TRACK_MODIFICATIONS=False,MAX_CONTENT_LENGTH=int(os.getenv('UPLOAD_MAX_MB','50'))*1024*1024,UPLOAD_FOLDER=os.path.join(app.root_path,'static','uploads'),SITE_URL=os.getenv('SITE_URL','https://ijny.com'),SESSION_COOKIE_HTTPONLY=True,SESSION_COOKIE_SAMESITE='Lax',SESSION_COOKIE_SECURE=os.getenv('COOKIE_SECURE','false').lower()=='true',REMEMBER_COOKIE_HTTPONLY=True,REMEMBER_COOKIE_SAMESITE='Lax')
    os.makedirs(app.config['UPLOAD_FOLDER'],exist_ok=True); db.init_app(app); login_manager.init_app(app); csrf.init_app(app); limiter.init_app(app); login_manager.login_view='auth.login'
    import json
    app.jinja_env.filters['fromjson']=lambda x: json.loads(x or '[]')
    app.jinja_env.globals['getattr']=getattr
    @app.context_processor
    def inject_site():
        from .models import MenuItem,SiteSetting,Notification
        settings={x.key:x.value for x in SiteSetting.query.all()}
        return {'menu_items':MenuItem.query.filter_by(menu='main',visible=True).order_by(MenuItem.sort_order).all(),'settings':settings,'site_name':settings.get('site_name','شبكة الصحفيين المستقلين في اليمن'),'site_short':settings.get('site_short','IJNY'),'unread_notifications': Notification.query.filter_by(user_id=getattr(__import__('flask_login').current_user,'id',None),read=False).count() if getattr(__import__('flask_login').current_user,'is_authenticated',False) else 0}
    from .routes import main_bp; from .auth import auth_bp; from .admin import admin_bp
    app.register_blueprint(main_bp); app.register_blueprint(auth_bp); app.register_blueprint(admin_bp)
    @app.after_request
    def headers(resp):
        resp.headers['X-Content-Type-Options']='nosniff'; resp.headers['X-Frame-Options']='SAMEORIGIN'; resp.headers['Referrer-Policy']='strict-origin-when-cross-origin'; return resp
    with app.app_context():
        db.create_all(); from .seed import seed; seed()
    return app
@login_manager.user_loader
def load_user(uid):
    from .models import User
    return db.session.get(User,int(uid))
