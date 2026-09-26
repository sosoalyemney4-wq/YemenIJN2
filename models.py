from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

role_permission=db.Table('role_permission',db.Column('role_id',db.Integer,db.ForeignKey('role.id'),primary_key=True),db.Column('permission_id',db.Integer,db.ForeignKey('permission.id'),primary_key=True))

class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(160),nullable=False); email=db.Column(db.String(255),unique=True,nullable=False,index=True)
    password_hash=db.Column(db.String(255),nullable=False); role_id=db.Column(db.Integer,db.ForeignKey('role.id')); active=db.Column(db.Boolean,default=True); must_change_password=db.Column(db.Boolean,default=True); created_at=db.Column(db.DateTime,default=datetime.utcnow); last_login=db.Column(db.DateTime)
    role=db.relationship('Role',backref='users')
    def set_password(self,p): self.password_hash=generate_password_hash(p)
    def check_password(self,p): return check_password_hash(self.password_hash,p)
class Role(db.Model):
    id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(80),unique=True); description=db.Column(db.Text); permissions=db.relationship('Permission',secondary=role_permission,backref='roles')
class Permission(db.Model):
    id=db.Column(db.Integer,primary_key=True); key=db.Column(db.String(100),unique=True); label=db.Column(db.String(180))
class Section(db.Model):
    id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(160),nullable=False); slug=db.Column(db.String(180),unique=True,nullable=False); description=db.Column(db.Text); image=db.Column(db.String(500)); icon=db.Column(db.String(500)); sort_order=db.Column(db.Integer,default=0); status=db.Column(db.String(30),default='published'); show_menu=db.Column(db.Boolean,default=True); show_home=db.Column(db.Boolean,default=True); seo_title=db.Column(db.String(255)); seo_description=db.Column(db.Text); created_at=db.Column(db.DateTime,default=datetime.utcnow); updated_at=db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)
    windows=db.relationship('Window',backref='section',cascade='all,delete-orphan',order_by='Window.sort_order')
class Window(db.Model):
    id=db.Column(db.Integer,primary_key=True); section_id=db.Column(db.Integer,db.ForeignKey('section.id'),nullable=False); name=db.Column(db.String(160),nullable=False); slug=db.Column(db.String(180),unique=True,nullable=False); description=db.Column(db.Text); image=db.Column(db.String(500)); icon=db.Column(db.String(500)); sort_order=db.Column(db.Integer,default=0); status=db.Column(db.String(30),default='published'); seo_title=db.Column(db.String(255)); seo_description=db.Column(db.Text); created_at=db.Column(db.DateTime,default=datetime.utcnow); updated_at=db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)
    articles=db.relationship('Article',backref='window',cascade='all,delete-orphan')
class Article(db.Model):
    id=db.Column(db.Integer,primary_key=True); window_id=db.Column(db.Integer,db.ForeignKey('window.id')); title=db.Column(db.String(300),nullable=False); slug=db.Column(db.String(320),unique=True,nullable=False); summary=db.Column(db.Text); content=db.Column(db.Text); cover_image=db.Column(db.String(500)); author=db.Column(db.String(160)); publish_at=db.Column(db.DateTime); published_at=db.Column(db.DateTime); governorate=db.Column(db.String(120)); region=db.Column(db.String(160)); content_type=db.Column(db.String(100)); topic=db.Column(db.String(160)); keywords=db.Column(db.Text); sources=db.Column(db.Text); attachments=db.Column(db.Text); related_materials=db.Column(db.Text); external_links=db.Column(db.Text); status=db.Column(db.String(30),default='draft'); editor=db.Column(db.String(160)); seo_title=db.Column(db.String(255)); seo_description=db.Column(db.Text); canonical_url=db.Column(db.String(600)); social_image=db.Column(db.String(500)); share_enabled=db.Column(db.Boolean,default=True); comments_enabled=db.Column(db.Boolean,default=True); pinned=db.Column(db.Boolean,default=False); featured=db.Column(db.Boolean,default=False); homepage=db.Column(db.Boolean,default=False); created_at=db.Column(db.DateTime,default=datetime.utcnow); updated_at=db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)
class Opportunity(db.Model):
    id=db.Column(db.Integer,primary_key=True); title=db.Column(db.String(300),nullable=False); slug=db.Column(db.String(320),unique=True,nullable=False); organization=db.Column(db.String(220)); opportunity_type=db.Column(db.String(100)); deadline=db.Column(db.DateTime); country=db.Column(db.String(120)); geography=db.Column(db.String(160)); target=db.Column(db.String(300)); eligibility=db.Column(db.Text); funding=db.Column(db.String(200)); currency=db.Column(db.String(30)); language=db.Column(db.String(100)); apply_url=db.Column(db.String(600)); add_date=db.Column(db.DateTime,default=datetime.utcnow); end_date=db.Column(db.DateTime); status=db.Column(db.String(30),default='open'); auto_status=db.Column(db.Boolean,default=True); description=db.Column(db.Text); image=db.Column(db.String(500)); seo_title=db.Column(db.String(255)); seo_description=db.Column(db.Text); created_at=db.Column(db.DateTime,default=datetime.utcnow); updated_at=db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)
class Resource(db.Model):
    id=db.Column(db.Integer,primary_key=True); title=db.Column(db.String(300),nullable=False); slug=db.Column(db.String(320),unique=True,nullable=False); category=db.Column(db.String(160)); resource_type=db.Column(db.String(100)); description=db.Column(db.Text); content=db.Column(db.Text); url=db.Column(db.String(600)); file_path=db.Column(db.String(500)); image=db.Column(db.String(500)); status=db.Column(db.String(30),default='published'); seo_title=db.Column(db.String(255)); seo_description=db.Column(db.Text); created_at=db.Column(db.DateTime,default=datetime.utcnow)
class Page(db.Model):
    id=db.Column(db.Integer,primary_key=True); title=db.Column(db.String(220)); slug=db.Column(db.String(220),unique=True); content=db.Column(db.Text); image=db.Column(db.String(500)); buttons=db.Column(db.Text); seo_title=db.Column(db.String(255)); seo_description=db.Column(db.Text); canonical_url=db.Column(db.String(600)); status=db.Column(db.String(30),default='published')
class HomepageBlock(db.Model):
    id=db.Column(db.Integer,primary_key=True); block_type=db.Column(db.String(80)); title=db.Column(db.String(220)); subtitle=db.Column(db.Text); settings=db.Column(db.Text); sort_order=db.Column(db.Integer,default=0); visible=db.Column(db.Boolean,default=True)
class MenuItem(db.Model):
    id=db.Column(db.Integer,primary_key=True); menu=db.Column(db.String(50)); label=db.Column(db.String(160)); url=db.Column(db.String(500)); icon=db.Column(db.String(500)); sort_order=db.Column(db.Integer,default=0); visible=db.Column(db.Boolean,default=True); parent_id=db.Column(db.Integer,db.ForeignKey('menu_item.id')); children=db.relationship('MenuItem',backref=db.backref('parent',remote_side=[id]))
class Media(db.Model):
    id=db.Column(db.Integer,primary_key=True); filename=db.Column(db.String(300)); path=db.Column(db.String(600)); mime=db.Column(db.String(120)); size=db.Column(db.Integer); kind=db.Column(db.String(50)); alt_text=db.Column(db.String(500)); title=db.Column(db.String(300)); uploaded_by=db.Column(db.Integer); created_at=db.Column(db.DateTime,default=datetime.utcnow)
class Author(db.Model):
    id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(180),nullable=False); slug=db.Column(db.String(180),unique=True,nullable=False); bio=db.Column(db.Text); image=db.Column(db.String(500)); email=db.Column(db.String(255)); active=db.Column(db.Boolean,default=True)
class Taxonomy(db.Model):
    id=db.Column(db.Integer,primary_key=True); taxonomy_type=db.Column(db.String(80)); name=db.Column(db.String(160)); slug=db.Column(db.String(180),unique=True); description=db.Column(db.Text); sort_order=db.Column(db.Integer,default=0)
class Membership(db.Model):
    id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(180)); email=db.Column(db.String(255)); phone=db.Column(db.String(80)); governorate=db.Column(db.String(120)); profile=db.Column(db.Text); portfolio=db.Column(db.String(600)); status=db.Column(db.String(40),default='pending'); created_at=db.Column(db.DateTime,default=datetime.utcnow)
class ContactMessage(db.Model):
    id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(180)); email=db.Column(db.String(255)); subject=db.Column(db.String(300)); message=db.Column(db.Text); attachment=db.Column(db.String(500)); status=db.Column(db.String(40),default='new'); created_at=db.Column(db.DateTime,default=datetime.utcnow)
class Violation(db.Model):
    id=db.Column(db.Integer,primary_key=True); journalist=db.Column(db.String(180)); violation_type=db.Column(db.String(180)); governorate=db.Column(db.String(120)); date=db.Column(db.DateTime); source=db.Column(db.String(500)); details=db.Column(db.Text); status=db.Column(db.String(40),default='documenting'); created_at=db.Column(db.DateTime,default=datetime.utcnow)
class Statement(db.Model):
    id=db.Column(db.Integer,primary_key=True); title=db.Column(db.String(300)); content=db.Column(db.Text); published_at=db.Column(db.DateTime); status=db.Column(db.String(40),default='draft'); seo_title=db.Column(db.String(255)); seo_description=db.Column(db.Text)
class AuditLog(db.Model):
    id=db.Column(db.Integer,primary_key=True); user_id=db.Column(db.Integer); action=db.Column(db.String(160)); entity=db.Column(db.String(100)); entity_id=db.Column(db.Integer); details=db.Column(db.Text); ip=db.Column(db.String(80)); created_at=db.Column(db.DateTime,default=datetime.utcnow)
class Notification(db.Model):
    id=db.Column(db.Integer,primary_key=True); user_id=db.Column(db.Integer); title=db.Column(db.String(240)); body=db.Column(db.Text); read=db.Column(db.Boolean,default=False); created_at=db.Column(db.DateTime,default=datetime.utcnow)
class Trash(db.Model):
    id=db.Column(db.Integer,primary_key=True); entity=db.Column(db.String(100)); entity_id=db.Column(db.Integer); snapshot=db.Column(db.Text); deleted_by=db.Column(db.Integer); created_at=db.Column(db.DateTime,default=datetime.utcnow)
class SiteSetting(db.Model):
    id=db.Column(db.Integer,primary_key=True); key=db.Column(db.String(120),unique=True); value=db.Column(db.Text)
