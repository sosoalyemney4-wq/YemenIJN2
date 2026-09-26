from flask import Blueprint,render_template,request,redirect,url_for,flash,Response,current_app
from .models import *
from . import db
from datetime import datetime
from sqlalchemy import or_,desc
main_bp=Blueprint('main',__name__)

def publish_scheduled():
    now=datetime.utcnow(); rows=Article.query.filter(Article.status.in_(['draft','pending']),Article.publish_at!=None,Article.publish_at<=now).all()
    for a in rows: a.status='published';a.published_at=now
    if rows: db.session.commit()

def public_articles(limit=12):
    publish_scheduled(); return Article.query.filter_by(status='published').order_by(desc(Article.published_at),desc(Article.created_at)).limit(limit).all()
@main_bp.get('/')
def home():
    blocks=HomepageBlock.query.filter_by(visible=True).order_by(HomepageBlock.sort_order).all(); return render_template('home.html',blocks=blocks,articles=public_articles(12),opportunities=Opportunity.query.filter_by(status='open').order_by(desc(Opportunity.deadline)).limit(8).all(),resources=Resource.query.filter_by(status='published').order_by(desc(Resource.created_at)).limit(8).all(),statements=Statement.query.filter_by(status='published').order_by(desc(Statement.published_at)).limit(5).all())
@main_bp.get('/section/<slug>')
def section(slug): return render_template('section.html',section=Section.query.filter_by(slug=slug,status='published').first_or_404())
@main_bp.get('/article/<slug>')
def article(slug): return render_template('article.html',article=Article.query.filter_by(slug=slug,status='published').first_or_404())
@main_bp.get('/opportunities')
def opportunities():
    items=Opportunity.query.order_by(desc(Opportunity.created_at)).all(); return render_template('opportunities.html',items=items)
@main_bp.get('/resources')
def resources(): return render_template('resources.html',items=Resource.query.order_by(desc(Resource.created_at)).all())
@main_bp.get('/search')
def search():
    q=request.args.get('q','').strip(); typ=request.args.get('type','');gov=request.args.get('governorate','');topic=request.args.get('topic',''); page=max(1,int(request.args.get('page',1))); per=12
    query=Article.query.filter_by(status='published')
    if q: query=query.filter(or_(Article.title.ilike(f'%{q}%'),Article.summary.ilike(f'%{q}%'),Article.content.ilike(f'%{q}%'),Article.keywords.ilike(f'%{q}%')))
    if typ: query=query.filter_by(content_type=typ)
    if gov: query=query.filter_by(governorate=gov)
    if topic: query=query.filter_by(topic=topic)
    pag=query.order_by(desc(Article.published_at)).paginate(page=page,per_page=per,error_out=False)
    return render_template('search.html',q=q,articles=pag.items,pagination=pag,types=[x[0] for x in db.session.query(Article.content_type).filter(Article.content_type!=None).distinct().all()],governorates=[x[0] for x in db.session.query(Article.governorate).filter(Article.governorate!=None).distinct().all()],topics=[x[0] for x in db.session.query(Article.topic).filter(Article.topic!=None).distinct().all()])
@main_bp.route('/join',methods=['GET','POST'])
def join():
    if request.method=='POST': db.session.add(Membership(name=request.form['name'],email=request.form['email'],phone=request.form.get('phone'),governorate=request.form.get('governorate'),profile=request.form.get('profile'),portfolio=request.form.get('portfolio')));db.session.commit();flash('تم استلام طلب العضوية');return redirect(url_for('main.join'))
    return render_template('join.html')
@main_bp.route('/contact',methods=['GET','POST'])
def contact():
    if request.method=='POST': db.session.add(ContactMessage(name=request.form['name'],email=request.form['email'],subject=request.form.get('subject'),message=request.form['message']));db.session.commit();flash('تم استلام الرسالة');return redirect(url_for('main.contact'))
    return render_template('contact.html')
@main_bp.get('/about')
def about(): return render_template('page.html',page=Page.query.filter_by(slug='about').first_or_404())
@main_bp.get('/sitemap.xml')
def sitemap():
    base=current_app.config['SITE_URL'].rstrip('/'); return render_template('sitemap.xml',base=base,sections=Section.query.filter_by(status='published').all(),articles=Article.query.filter_by(status='published').all(),pages=Page.query.filter_by(status='published').all(),mimetype='application/xml')
@main_bp.get('/health')
def health(): return {'status':'ok','site':'IJNY','database':'ok'},200
@main_bp.get('/robots.txt')
def robots(): return Response(f"User-agent: *\nAllow: /\nDisallow: /control/\nDisallow: /auth/\nSitemap: {current_app.config['SITE_URL'].rstrip('/')}/sitemap.xml\n",mimetype='text/plain')
