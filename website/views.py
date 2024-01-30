from flask import Blueprint, render_template, request, flash, url_for, redirect

from .func import get_contact_info, get_about_info
from .models import Services, Projects, TeamMember, Testimonial, Quote, Subscriber
from .mail import send_email, mail_to

from json import load
from threading import Thread

views = Blueprint('views', __name__)

@views.errorhandler(404)
def error_404(e):
    """
    404 hata kodu için template içindeki 404.html dosyasını döndürür
    """
    return render_template('404.html'), 404

@views.route('/')
def home():
    """
    Anasayfa
    """
    return render_template('index.html', 
                           services=Services.select().order_by(Services.id.desc()),
                           projects=Projects.select().limit(6),
                           about=get_about_info(),
                           members=TeamMember.select().order_by(TeamMember.id.desc()).limit(4),
                           testimonials=Testimonial.select().order_by(Testimonial.id.desc()).limit(3),)
    # Anasayfada çok kalabalık olmaması için bazı veriler sınırlı olarak eklendi

@views.route('/contact')
def contact():
    """
    İletişim sayfası
    """
    return render_template('contact.html',
                           services=Services.select())

@views.route('/about')
def about():
    """
    Hakkında sayfası
    """
    return render_template('about.html', 
                           about=get_about_info(),
                           members=TeamMember.select().order_by(TeamMember.id.desc()).limit(4))

@views.route('/service')
def service():
    """
    Servisler sayfası
    """
    return render_template('service.html', 
                           services=Services.select(),
                           testimonials=Testimonial.select().order_by(Testimonial.id.desc()).limit(3))

@views.route('/project')
def project():
    """
    Projeler sayfası
    """
    return render_template('project.html', projects=Projects.select())

@views.route('/our-team')
def team():
    """
    Ekibimiz sayfası
    """
    return render_template('team.html', teamMembers=TeamMember.select())

@views.route('/testimonial')
def testimonial():
    """
    Referanslar sayfası
    """
    return render_template('testimonial.html', testimonials=Testimonial.select())

@views.route('/feature')
def feature():
    """
    Özellik sayfası
    """    
    return render_template('feature.html')

@views.route('/quote', methods=['POST', 'GET'])
def quote():
    """
    Get ve Post methodlarını kullanıyor
    Teklif gönderme sayfası
    """
    if request.method == 'GET':
        return render_template('quote.html',
                               services = Services.select())
    else:
        name = request.form.get('name')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        service = request.form.get('service')
        note = request.form.get('note')
        # Form verileri değişkene kaydediliyor

        if len(name)>100:
            flash('Lütfen isim 100 karakterden daha az olsun')
            return redirect(url_for('views.quote'))
        
        if len(email)>100:
            flash('Lütfen mail 100 karakterden daha az olsun')
            return redirect(url_for('views.quote'))
        
        if len(mobile)>100:
            flash('Lütfen mobile 100 karakterden daha az olsun')
            return redirect(url_for('views.quote'))
        
        if len(service)>100:
            flash('Lütfen bir servis seçin!')
            return redirect(url_for('views.quote'))
        
        if len(note)>100:
            flash('Lütfen not 700 karakterden daha az olsun')
            return redirect(url_for('views.quote'))
        
        # Form verileri şartlara uyuyor mu kontrol ediliyor
        
        quote = Quote.create(name=name,
                            email=email,
                            mobile=mobile,
                            service=service,
                            note=note)
        
        # Database'e kaydediliyor
        
        url = request.root_url[:-1]+url_for('admin.view_quote', pk=quote.id)
        Thread(target= lambda url: send_email("Yeni iletiniz var!",
                    f"""
                    <a href="{url}">Görüntülemek için tıklayın!</a>
                    """), args=[url]).start()
        # Asenkron biçimde sistem yöneticisine mail atılıyor


        flash('Notunuz başarıyla iletildi')
        return redirect(url_for('views.home'))
    
@views.route('/register-subscriber', methods=['POST'])
def register_subscriber():
    mail = request.form.get('mail').strip().lower()
    # Mail adresini form verilerinden alıyorum

    Subscriber.get_or_create(email=mail)
    # Database'e eğer kayıtlı değilse kayıt ediyorum.

    flash('Başarıyla kayıt oldunuz!')
    return redirect(url_for('views.home'))
    # Kullanıcıyı ana sayfaya yönlendiriyorum
