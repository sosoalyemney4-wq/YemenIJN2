import os,uuid,json,datetime,shutil
from flask import Blueprint,render_template,request,redirect,url_for,flash,current_app,abort,jsonify
from flask_login import login_required,current_user
from werkzeug.utils import secure_filename
from sqlalchemy import desc
from . import db
from .models import *
import bleach
admin_bp=Blueprint('admin',__name__,url_prefix='/control')

def ok(perm='content.edit'):
    if not current_user.is_authenticated or not current_user.role:return False
    return current_user.role.name=='Super Admin' or any(p.key==perm for p in current_user.role.permissions)
def guard(perm='content.edit'):
    if not ok(perm): abort(403)
def audit(action,entity,eid=None,details=''):
    db.session.add(AuditLog(user_id=current_user.id,action=action,entity=entity,entity_id=eid,details=details,ip=request.remote_addr));db.session.commit()
def parse_dt(v):
    if not v:return None
    try:return datetime.datetime.fromisoformat(v.replace('Z',''))
    except:return None
def slugify(v):
    import re
    v=(v or '').strip().lower();v=re.sub(r'[^\w\u0600-\u06ff-]+','-',v,flags=re.UNICODE);return v.strip('-')
MODELS={'sections':Section,'windows':Window,'articles':Article,'opportunities':Opportunity,'resources':Resource,'authors':Author,'taxonomy':Taxonomy,'violations':Violation,'statements':Statement,'pages':Page,'members':Membership,'messages':ContactMessage,'users':User,'roles':Role,'notifications':Notification,'audit':AuditLog,'trash':Trash,'menus':MenuItem,'homepage':HomepageBlock}

@admin_bp.get('/')
@login_required
def dashboard():
    guard('audit.view'); counts={k:cls.query.count() for k,cls in {'articles':Article,'sections':Section,'windows':Window,'opportunities':Opportunity,'resources':Resource,'members':Membership,'messages':ContactMessage,'media':Media,'violations':Violation,'statements':Statement,'users':User}.items()}; return render_template('admin/dashboard.html',counts=counts)

@admin_bp.route('/<entity>',methods=['GET','POST'])
@login_required
def entity_list(entity):
    cls=MODELS.get(entity)
    if not cls: abort(404)
    guard('users.manage' if entity in ['users','roles'] else 'content.edit')
    if request.method=='POST':
        obj=cls()
        fields=[c.name for c in cls.__table__.columns if c.name not in ['id','created_at','updated_at','last_login']]
        for f in fields:
            if f not in request.form: continue
            val=request.form.get(f)
            if f in ['active','visible','show_menu','show_home','auto_status','share_enabled','comments_enabled','pinned','featured','homepage']: val=f in request.form
            elif f.endswith('_id') or f in ['sort_order','parent_id','role_id','section_id','window_id','user_id','uploaded_by','deleted_by']: val=int(val) if val else None
            elif f in ['publish_at','published_at','deadline','end_date','add_date','date']: val=parse_dt(val)
            if f in ['content','description','details','body','eligibility','summary'] and isinstance(val,str): val=bleach.clean(val, tags=['p','br','strong','em','u','h1','h2','h3','h4','ul','ol','li','blockquote','a','img','table','thead','tbody','tr','th','td','iframe','figure','figcaption'], attributes={'a':['href','target','rel'],'img':['src','alt','width','height'],'iframe':['src','width','height','allow','allowfullscreen','frameborder']}, protocols=['http','https','mailto'])
            setattr(obj,f,val)
        if hasattr(obj,'slug') and not getattr(obj,'slug'): obj.slug=slugify(getattr(obj,'name',getattr(obj,'title','item')))
        if hasattr(obj,'password_hash') and request.form.get('password'): obj.set_password(request.form['password']);obj.must_change_password=True
        db.session.add(obj);db.session.commit();audit('create',entity,obj.id);flash('تم الحفظ بنجاح');return redirect(url_for('admin.entity_list',entity=entity))
    items=cls.query.order_by(desc(getattr(cls,'created_at',getattr(cls,'sort_order',cls.id)))).all() if hasattr(cls,'created_at') else cls.query.order_by(getattr(cls,'sort_order',cls.id)).all()
    return render_template('admin/entity.html',entity=entity,title=entity_title(entity),items=items,fields=field_specs(entity),model=cls)

def entity_title(e): return {'sections':'الأقسام','windows':'النوافذ','articles':'المقالات والتحقيقات','opportunities':'الفرص','resources':'الموارد','authors':'الصحفيون والكتاب','taxonomy':'التصنيفات والوسوم','violations':'انتهاكات الصحفيين','statements':'بيانات الشبكة','pages':'الصفحات','members':'طلبات العضوية','messages':'رسائل التواصل','users':'المستخدمون','roles':'الأدوار والصلاحيات','notifications':'الإشعارات','audit':'سجل التدقيق','trash':'سلة المحذوفات','menus':'القوائم والتذييل','homepage':'منشئ الصفحة الرئيسية'}.get(e,e)
def field_specs(e):
    d={'sections':[('name','اسم القسم','text'),('slug','الرابط','text'),('description','الوصف','textarea'),('image','الصورة','text'),('icon','الأيقونة','text'),('sort_order','الترتيب','number'),('status','الحالة','select'),('show_menu','في القائمة','check'),('show_home','في الرئيسية','check'),('seo_title','SEO title','text'),('seo_description','SEO description','textarea')],
    'windows':[('section_id','القسم','number'),('name','اسم النافذة','text'),('slug','الرابط','text'),('description','الوصف','textarea'),('image','الصورة','text'),('icon','الأيقونة','text'),('sort_order','الترتيب','number'),('status','الحالة','select'),('seo_title','SEO title','text'),('seo_description','SEO description','textarea')],
    'articles':[('window_id','النافذة','number'),('title','العنوان','text'),('slug','الرابط','text'),('summary','الملخص','textarea'),('content','المحتوى HTML','editor'),('cover_image','صورة الغلاف','text'),('author','الكاتب','text'),('publish_at','موعد النشر','datetime-local'),('governorate','المحافظة','text'),('region','المنطقة','text'),('content_type','نوع المحتوى','text'),('topic','الموضوع','text'),('keywords','الكلمات المفتاحية','text'),('sources','المصادر','textarea'),('external_links','الروابط الخارجية','textarea'),('status','الحالة','select'),('editor','المحرر','text'),('seo_title','SEO title','text'),('seo_description','SEO description','textarea'),('canonical_url','Canonical URL','text'),('social_image','الصورة الاجتماعية','text'),('share_enabled','المشاركة','check'),('comments_enabled','التعليقات','check'),('pinned','مثبت','check'),('featured','مميز','check'),('homepage','في الرئيسية','check')],
    'opportunities':[('title','العنوان','text'),('slug','الرابط','text'),('organization','الجهة','text'),('opportunity_type','نوع الفرصة','text'),('deadline','الموعد النهائي','datetime-local'),('country','الدولة','text'),('geography','النطاق الجغرافي','text'),('target','الفئة المستهدفة','text'),('eligibility','شروط الأهلية','textarea'),('funding','التمويل','text'),('currency','العملة','text'),('language','اللغة','text'),('apply_url','رابط التقديم','text'),('description','الوصف','textarea'),('status','الحالة','select'),('auto_status','تحديث تلقائي','check'),('seo_title','SEO title','text'),('seo_description','SEO description','textarea')],
    'resources':[('title','العنوان','text'),('slug','الرابط','text'),('category','التصنيف','text'),('resource_type','نوع المورد','text'),('description','الوصف','textarea'),('content','المحتوى','editor'),('url','الرابط','text'),('file_path','الملف','text'),('image','الصورة','text'),('status','الحالة','select'),('seo_title','SEO title','text'),('seo_description','SEO description','textarea')],
    'authors':[('name','الاسم','text'),('slug','الرابط','text'),('bio','السيرة','textarea'),('image','الصورة','text'),('email','البريد','text'),('active','نشط','check')],
    'taxonomy':[('taxonomy_type','النوع','text'),('name','الاسم','text'),('slug','الرابط','text'),('description','الوصف','textarea'),('sort_order','الترتيب','number')],
    'violations':[('journalist','الصحفي','text'),('violation_type','نوع الانتهاك','text'),('governorate','المحافظة','text'),('date','التاريخ','datetime-local'),('source','المصدر','text'),('details','التفاصيل','textarea'),('status','الحالة','text')],
    'statements':[('title','العنوان','text'),('content','المحتوى','editor'),('published_at','تاريخ النشر','datetime-local'),('status','الحالة','select'),('seo_title','SEO title','text'),('seo_description','SEO description','textarea')],
    'pages':[('title','العنوان','text'),('slug','الرابط','text'),('content','المحتوى','editor'),('image','الصورة','text'),('buttons','أزرار JSON','textarea'),('seo_title','SEO title','text'),('seo_description','SEO description','textarea'),('canonical_url','Canonical URL','text'),('status','الحالة','select')],
    'menus':[('menu','القائمة','text'),('label','النص','text'),('url','الرابط','text'),('icon','الأيقونة','text'),('sort_order','الترتيب','number'),('visible','ظاهر','check')],
    'homepage':[('block_type','نوع البلوك','text'),('title','العنوان','text'),('subtitle','الوصف','textarea'),('settings','الإعدادات JSON','textarea'),('sort_order','الترتيب','number'),('visible','ظاهر','check')],
    'users':[('name','الاسم','text'),('email','البريد','text'),('role_id','رقم الدور','number'),('password','كلمة المرور','password'),('active','نشط','check')],
    'roles':[('name','اسم الدور','text'),('description','الوصف','textarea')],
    'notifications':[('user_id','المستخدم','number'),('title','العنوان','text'),('body','النص','textarea')],
    }
    return d.get(e,[('status','الحالة','text')])

@admin_bp.route('/<entity>/<int:id>/edit',methods=['GET','POST'])
@login_required
def entity_edit(entity,id):
    cls=MODELS.get(entity)
    if not cls: abort(404)
    guard('users.manage' if entity in ['users','roles'] else 'content.edit')
    obj=db.session.get(cls,id)
    if not obj: abort(404)
    fields=field_specs(entity)
    if request.method=='POST':
        for f,label,typ in fields:
            if f not in request.form: continue
            val=request.form.get(f)
            if typ=='check': val=f in request.form
            elif typ in ['number']: val=int(val) if val else None
            elif typ=='datetime-local': val=parse_dt(val)
            if f in ['content','description','details','body','eligibility','summary'] and isinstance(val,str): val=bleach.clean(val,tags=['p','br','strong','em','u','h1','h2','h3','h4','ul','ol','li','blockquote','a','img','table','thead','tbody','tr','th','td','iframe','figure','figcaption'],attributes={'a':['href','target','rel'],'img':['src','alt','width','height'],'iframe':['src','width','height','allow','allowfullscreen','frameborder']},protocols=['http','https','mailto'])
            if f=='password' and val:
                obj.set_password(val); obj.must_change_password=True; continue
            setattr(obj,f,val)
        if hasattr(obj,'slug') and not getattr(obj,'slug'): obj.slug=slugify(getattr(obj,'name',getattr(obj,'title','item')))
        db.session.commit();audit('update',entity,id);flash('تم تحديث العنصر');return redirect(url_for('admin.entity_list',entity=entity))
    return render_template('admin/edit.html',entity=entity,title=entity_title(entity),obj=obj,fields=fields)

@admin_bp.post('/<entity>/<int:id>/delete')
@login_required
def entity_delete(entity,id):
    guard('content.delete'); cls=MODELS.get(entity); obj=db.session.get(cls,id) if cls else None
    if not obj: abort(404)
    snap={c.name:getattr(obj,c.name) for c in cls.__table__.columns if c.name!='password_hash'}; db.session.add(Trash(entity=entity,entity_id=id,snapshot=json.dumps(snap,default=str,ensure_ascii=False),deleted_by=current_user.id));db.session.delete(obj);db.session.commit();audit('delete',entity,id);flash('تم النقل إلى سلة المحذوفات');return redirect(url_for('admin.entity_list',entity=entity))

@admin_bp.post('/reorder/<entity>')
@login_required
def reorder(entity):
    guard('content.edit'); cls=MODELS.get(entity); ids=request.form.getlist('ids[]') or request.form.getlist('ids');
    for i,sid in enumerate(ids):
        obj=db.session.get(cls,int(sid));
        if obj and hasattr(obj,'sort_order'): obj.sort_order=i
    db.session.commit();return jsonify(ok=True)

@admin_bp.get('/media')
@login_required
def media(): guard('media.manage'); q=request.args.get('q',''); items=Media.query.filter(Media.filename.ilike(f'%{q}%')).order_by(desc(Media.created_at)).all() if q else Media.query.order_by(desc(Media.created_at)).all(); return render_template('admin/media.html',items=items)
@admin_bp.post('/media/upload')
@login_required
def upload_media():
    guard('media.manage'); f=request.files.get('file'); allowed={'image/jpeg','image/png','image/webp','image/gif','application/pdf','video/mp4','audio/mpeg','audio/wav','font/woff','font/woff2','font/ttf','font/otf','application/zip'}
    if not f or not f.filename or f.mimetype not in allowed: flash('الملف غير صالح أو نوعه غير مسموح');return redirect(url_for('admin.media'))
    ext=os.path.splitext(secure_filename(f.filename))[1].lower(); name=uuid.uuid4().hex+ext; path=os.path.join(current_app.config['UPLOAD_FOLDER'],name);f.save(path);kind='font' if ext in ['.ttf','.otf','.woff','.woff2'] else ('image' if f.mimetype.startswith('image/') else 'file');m=Media(filename=secure_filename(f.filename),path='/static/uploads/'+name,mime=f.mimetype,size=os.path.getsize(path),kind=kind,uploaded_by=current_user.id);db.session.add(m);db.session.commit();audit('upload','media',m.id,m.filename);flash('تم رفع الملف');return redirect(url_for('admin.media'))
@admin_bp.post('/media/<int:id>/delete')
@login_required
def media_delete(id):
    guard('media.manage');m=db.session.get(Media,id)
    if m:
        p=os.path.join(current_app.root_path,m.path.lstrip('/'))
        if os.path.exists(p):os.remove(p)
        db.session.delete(m);db.session.commit();audit('delete','media',id)
    return redirect(url_for('admin.media'))
@admin_bp.get('/settings')
@login_required
def settings(): guard('settings.manage');return render_template('admin/settings.html',title='إعدادات الموقع')
@admin_bp.post('/settings')
@login_required
def settings_save():
    guard('settings.manage')
    for k,v in request.form.items():
        s=SiteSetting.query.filter_by(key=k).first() or SiteSetting(key=k);s.value=v;db.session.add(s)
    db.session.commit();audit('update','settings',None,'site settings');flash('تم حفظ الإعدادات');return redirect(url_for('admin.settings'))
@admin_bp.get('/design')
@login_required
def design(): guard('settings.manage');return render_template('admin/design.html')
@admin_bp.post('/design')
@login_required
def design_save():
    guard('settings.manage')
    for k in ['primary_color','secondary_color','accent_color','site_name','site_short','footer_text','support_text']:
        s=SiteSetting.query.filter_by(key=k).first() or SiteSetting(key=k);s.value=request.form.get(k,'');db.session.add(s)
    db.session.commit();flash('تم حفظ الهوية والتصميم');return redirect(url_for('admin.design'))
@admin_bp.get('/fonts')
@login_required
def fonts(): guard('media.manage');return redirect(url_for('admin.media'))
@admin_bp.get('/icons')
@login_required
def icons(): guard('media.manage');return redirect(url_for('admin.media'))
@admin_bp.get('/seo')
@login_required
def seo(): guard('seo.manage');return render_template('admin/settings.html',title='SEO')
@admin_bp.get('/about')
@login_required
def about_edit(): guard('content.edit');return redirect(url_for('admin.entity_list',entity='pages'))
@admin_bp.get('/menus')
@login_required
def menus(): guard('content.edit');return redirect(url_for('admin.entity_list',entity='menus'))
@admin_bp.get('/homepage')
@login_required
def homepage(): guard('content.edit');return redirect(url_for('admin.entity_list',entity='homepage'))
