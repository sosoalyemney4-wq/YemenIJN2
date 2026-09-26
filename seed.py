from . import db
from .models import *

def seed():
    perms=[('content.create','إنشاء المحتوى'),('content.edit','تعديل المحتوى'),('content.delete','حذف المحتوى'),('content.publish','النشر'),('media.manage','إدارة الوسائط'),('users.manage','إدارة المستخدمين'),('settings.manage','إدارة الإعدادات'),('seo.manage','إدارة SEO'),('audit.view','سجل التدقيق'),('taxonomy.manage','إدارة التصنيفات')]
    for k,l in perms:
        if not Permission.query.filter_by(key=k).first(): db.session.add(Permission(key=k,label=l))
    db.session.flush()
    superr=Role.query.filter_by(name='Super Admin').first()
    if not superr:
        superr=Role(name='Super Admin',description='صلاحيات كاملة'); superr.permissions=Permission.query.all(); db.session.add(superr); db.session.flush()
        for n in ['Admin','Editor','Journalist','Contributor','Moderator']:
            r=Role(name=n,description='دور مخصص'); r.permissions=Permission.query.filter(Permission.key.in_(['content.create','content.edit','media.manage'] if n in ['Journalist','Contributor'] else ['content.create','content.edit','content.publish','media.manage'])).all(); db.session.add(r)
    u=User.query.filter_by(email='admin@example.com').first()
    if not u:
        u=User(name='مدير النظام',email='admin@example.com',role=superr);u.set_password('ChangeMe!12345');u.must_change_password=True;db.session.add(u)
    if not Section.query.first():
        data=[('الصحافة','press','التحقيقات والتقارير والقصص والبيانات والوسائط'),('الفرص','opportunities','منح وزمالات ووظائف وتدريب'),('الموارد','resources','أدلة وتقارير وأدوات ودورات'),('الحماية والشبكة','protection','السلامة والدعم القانوني وبيانات الشبكة')]
        for i,(n,s,d) in enumerate(data):
            sec=Section(name=n,slug=s,description=d,sort_order=i);db.session.add(sec);db.session.flush()
            windows_by_section={
                'press':[('التحقيقات','investigations'),('التقارير والقصص','reports'),('قصص البيانات','data-stories'),('التحقيقات المشتركة','joint-investigations'),('الوسائط المتعددة','multimedia')],
                'opportunities':[('منح وتمويل','funding'),('زمالات','fellowships'),('وظائف','jobs'),('تدريب ودورات','training')],
                'resources':[('الصحافة والتحقيق','journalism'),('الصحافة الرقمية والإعلام الجديد','digital'),('الذكاء الاصطناعي للصحفيين','ai'),('البيانات والتحقق والتضليل','verification'),('السلامة والحماية','safety')],
                'protection':[('السلامة المهنية','professional-safety'),('السلامة الرقمية والميدانية','digital-field-safety'),('الدعم القانوني','legal-support'),('انتهاكات الصحفيين','violations'),('بيانات ومواقف الشبكة','statements'),('من نحن','about')]
            }
            for j,w in enumerate(windows_by_section[s]): db.session.add(Window(section_id=sec.id,name=w[0],slug=w[1],sort_order=j))
    if not Page.query.filter_by(slug='about').first(): db.session.add(Page(title='من نحن',slug='about',content='<p>شبكة مستقلة للصحفيين في اليمن</p>'))
    if not HomepageBlock.query.first():
        for i,(t,title) in enumerate([('hero','شبكة الصحفيين المستقلين في اليمن'),('latest','أحدث المواد'),('opportunities','أحدث الفرص'),('resources','أحدث الموارد'),('network','أخبار وبيانات الشبكة'),('join','انضم إلى الشبكة'),('support','دعم الصحافة المستقلة'),('contact','تواصل معنا')]): db.session.add(HomepageBlock(block_type=t,title=title,sort_order=i))
    if not MenuItem.query.first():
        for i,(l,u) in enumerate([('الرئيسية','/'),('الصحافة','/section/press'),('الفرص','/opportunities'),('الموارد','/resources'),('الحماية والشبكة','/section/protection'),('البحث','/search')]): db.session.add(MenuItem(menu='main',label=l,url=u,sort_order=i))
    defaults={'site_name':'شبكة الصحفيين المستقلين في اليمن','site_short':'IJNY','primary_color':'#0b607d','secondary_color':'#19a7b9','accent_color':'#d8ad55','support_text':'دعم الصحافة المستقلة وحماية الصحفيين في اليمن','footer_text':'IJNY — شبكة الصحفيين المستقلين في اليمن'}
    for k,v in defaults.items():
        if not SiteSetting.query.filter_by(key=k).first(): db.session.add(SiteSetting(key=k,value=v))
    db.session.commit()
