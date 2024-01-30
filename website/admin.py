from flask import Blueprint, session, request, redirect, url_for, flash, render_template

from json import dumps
from os import remove
from shutil import rmtree
from threading import Thread

from .models import Services, Projects, TeamMember, Testimonial, Quote, Subscriber
from .decorators import loged_in_required
from .mail import send_email_subscribers
from .func import get_about_info, get_extension, get_image_path

admin = Blueprint('admin', __name__)

@admin.before_app_request
def admin_before_request():
    """
    Bu fonksiyon ile admin sayfalarına giriş yapılmadan girilemeyecek.
    """
    if str(request.url_rule).startswith('/admin/') and not ('id' in session.keys()):
        flash('You have not access to admin panel')
        return redirect(url_for('views.home'))

@admin.route('/panel')
def panel():
    """
    Panel sayfasını render ediyor. Sayfayı render ederken bir kaç değişkeni de gönderiyor. 
    Bu sayede sayfa render olurken aynı zamanda database ile iletişim kuruyor.
    """
    return render_template('admin/panel.html', 
                           about=get_about_info(), 
                           services=Services.select(),
                           projects=Projects.select(),
                           members=TeamMember.select(),
                           testimonials=Testimonial.select(),
                           quotes=Quote.select(),
                           subscribers_count = Subscriber.select().count())

@admin.route('change-contact-info', methods=['POST'])
def change_contact_info():
    """
    Sadece Post method kullanılıyor.
    Contact info ile ilgili herhangi bir değişikliği kayıt etmek isterseniz buraya yönlendiriyor.
    """
    data = {
        'adress': request.form.get('adress').strip(),
        'text': request.form.get('text').strip(),
        'work_times': request.form.get('work-times').strip(),
        'phone_number': request.form.get('phone-number').strip(),
        'links': {
            'facebook': request.form.get('facebook-link').strip(),
            'linkedin': request.form.get('linkedin-link').strip(),
            'twitter': request.form.get('twitter-link').strip(),
            'instagram': request.form.get('instagram-link').strip(),
            'google_maps': request.form.get('map-link').strip()
        }
    }
    """İlk olarak bir dictionary değişkenine çeviriyorum. 
    Strip methodları sayesinde başında ve sonundaki boşlukları siliyorum."""
    
    open('website/contact.json', 'w', encoding='utf-8').write(dumps(data, indent=4))
    # Bu komutla beraber değişkeni json dosyasına kayıt ediyorum

    flash('Başarıyla kaydedildi')
    return redirect(url_for('admin.panel'))
    # Kullanıcıyı panele yönlendiriyorum

@admin.route('change-about-info', methods=['POST'])
def change_about_info():
    """
    Sadece post methodu kullanılıyor.
    about info ile ilgili herhangi bir değişikliği kayıt etmek isterseniz buraya yönlendiriyor.
    """
    data = {
        'text': request.form.get('text').strip(),
        'happy_clients': request.form.get('happy-clients'),
        'projects_done': request.form.get('projects-done')
    }
    """İlk olarak bir dictionary değişkenine çeviriyorum. 
    Strip methodları sayesinde başında ve sonundaki boşlukları siliyorum."""

    open('website/about.json', 'w', encoding='utf-8').write(dumps(data, indent=4))
    # Bu komutla beraber değişkeni json dosyasına kayıt ediyorum

    flash('Başarıyla kaydedildi')
    return redirect(url_for('admin.panel'))
    # Kullanıcıyı panele yönlendiriyorum

@admin.route('add-services', methods=['GET', 'POST'])
def add_services():
    """ 
    Get ve post methodu kullanılıyor
    """
    if request.method == 'GET':
        # Eğer kullanıcı get methodu yaptıysa sayfayı render et
        return render_template('admin/add_services.html')
    else:
        # Eğer kullanıcı post methodu yaptıysa
        title = request.form.get('title').strip()
        description = request.form.get('description').strip()
        file = request.files['image']
        # Bütün form verilerini değişkene aktarıyorum

        if len(title) > 200 and len(description) > 500 :
            # Form verilerini validate ediyorum. Eğer validate başarısız olursa tekrar eklemeleri için yönlendiriyorum.
            flash('Lütfen başlığı 200 karakter ve açıklamayı 500 karakterden az tutun!')
            return redirect(url_for('admin.add_services'))
        
        if not file:
            # Görsel yüklemedilerse yönlendiriyorum.
            flash('Lütfen bir görsel yükleyin!')
            return redirect(url_for('admin.add_services'))
        
        service = Services(title=title, description=description)
        service.save()
        # Değişkeni database'e kaydediyorum

        file.save(f'website/custom_img/services/{service.id}/service.{get_extension(file.filename)}')
        # Kullanıcının gönderdiği görseli kayıt ediyorum

        return redirect(url_for('views.service'))
        # Kullanıcıyı yönlendiriyorum

@admin.route('edit-service/<int:pk>', methods=['GET', 'POST'])
def edit_service(pk):
    """
    Get ve Post methodu kullanılıyor
    Servis düzenleme
    Hangi servisi düzenleyeceğini tespit etmek için önce url üzerinden primary key(id) 
    numarasını alıyor.
    """
    service = Services.get_or_none(Services.id == pk)
    # Servisi databaseden alıyor

    if not service:
        flash('Servis bulunamadı!')
        return redirect(url_for('Servis bulunamadı!'))
    # Servis geçerli mi kontrolü

    if request.method == 'GET':
        return render_template('admin/edit_services.html', service=service)
    else:
        title = request.form.get('title')
        description = request.form.get('description')
        file = request.files['image']
        # Form verileri değişkene aktarılıyor

        if len(title) > 200 and len(description) > 500 :
            flash('Lütfen başlığı 200 karakter ve açıklamayı 500 karakterden az tutun!')
            return redirect(url_for('admin.add_services'))
        # Form verileri istenen şartlara uyuyor mu kontrol ediliyor
        
        if file:
            old_image_path = get_image_path('services', pk)
            remove('website/'+old_image_path)

            file.save(f'website/custom_img/services/{service.id}/service.{get_extension(file.filename)}')
        # Eğer görsel gönderilmişse eskisi silinip yenisi yükleniyor

        service.title = title
        service.description = description

        service.save()
        # Database'e kaydediliyor

        return redirect(url_for('views.service'))


@admin.route('delete-service/<pk>')
def delete_service(pk):
    service = Services.get_or_none(Services.id == pk)
    # Servis database'den çekiliyor

    if not service:
        return "<h1>Service not founded</h1>", 404
    # Servis geçerli mi kontrol ediliyor

    rmtree(f'website/custom_img/services/{service.id}')
    service.delete_instance()
    # Servis görselleri ve database'deki servis bilgileri siliniyor

    flash('Başarıyla silindi!')
    return redirect(url_for('views.service'))
    
@admin.route('add-project/', methods=['POST', 'GET'])
def add_project():
    """
    Get ve Post methodu kullanılıyor
    Proje ekleme
    """
    if request.method=='GET':
        return render_template('admin/add_project.html')
    else:
        title = request.form.get('title')
        project_type = request.form.get('carpentry')
        file = request.files['image']
        # Form verileri değişkene kaydediliyor

        if len(title) > 200 and not (project_type in ('General Carpentry', 'Custom Carpentry')) :
            flash('Lütfen başlığı 200 karakterden az tutun!')
            return redirect(url_for('admin.add_project'))
        # İstenen şartlar sağlanıyor mu kontrol ediliyor.

        if not file:
            flash('Lütfen bir görsel yükleyin!')
            return redirect(url_for('admin.add_project'))
        # Eğer görsel yok ise kullanıcıyı uyarıp yölendiriyor

        project = Projects(title=title, type=project_type)
        project.save()
        # Projeyi database'e ekliyor

        file.save(f'website/custom_img/projects/{project.id}/project.{get_extension(file.filename)}')
        # Fotoğrafı kayıt ediyor

        return redirect(url_for('views.project'))

@admin.route('edit-project/<pk>', methods=['GET', 'POST'])
def edit_project(pk):
    """
    Get ve Post methodu kullanılıyor
    Proje düzenleme
    Hangi projeyi düzenleyeceğini tespit etmek için önce url üzerinden primary key(id) 
    numarasını alıyor.
    """
    project = Projects.get_or_none(Projects.id == pk)
    # Projeyi database'den alıyor

    if not project:
        flash('Proje bulunamadı')
        return redirect('admin.panel')
    # Proje geçerli değilse yönlendiriyor
    
    if request.method == 'GET':
        return render_template('admin/edit_project.html', project=project)
    else:
        title = request.form.get('title')
        project_type = request.form.get('carpentry')
        file = request.files['image']
        # Form verilerini kullanıcıdan alıyor

        if len(title) > 200 and not (project_type in ('General Carpentry', 'Custom Carpentry')) :
            flash('Lütfen başlığı 200 karakterden az tutun!')
            return redirect(url_for('admin.edit_project', pk=pk))
        # Form verilieri geçerli mi kontrol ediliyor

        if file:
            old_image_path = get_image_path('projects', project.id)
            remove('website/'+old_image_path)

            file.save(f'website/custom_img/projects/{project.id}/project.{get_extension(file.filename)}')
        # Eğer görsel yüklendiyse ekisi silinip kaydediliyor


        project.title = title
        project.type = project_type

        project.save()
        # Değişiklikler database'e kaydediliyor

        return redirect(url_for('views.project'))

@admin.route('delete-project/<pk>')
def delete_project(pk):
    """
    Proje silme
    """
    project = Projects.get_or_none(Projects.id == pk)
    # Projeyi database'den alıyor

    if not project:
        flash('Proje bulunamadı!')
        return redirect(url_for('admin.panel'))
    # Proje geçerli değilse yönlendiriyor

    rmtree(f'website/custom_img/projects/{project.id}')
    project.delete_instance()
    # Projeyi ve görsel dosyalarını siliyor

    flash('Başarıyla silindi')
    return redirect(url_for('admin.panel'))

@admin.route('add-member', methods=['POST', 'GET'])
def add_member():
    """
    Get ve Post methodu kullanılıyor
    """
    if request.method == 'GET':
        return render_template('admin/add_member.html')
    else:
        name = request.form.get('name')
        designation = request.form.get('designation')

        fb_link = request.form.get('fb-link')
        t_link = request.form.get('t-link')
        i_link = request.form.get('i-link')
        
        file = request.files['image']
        # Form verileri değişkenlere kaydediliyor

        if len(name) > 200:
            flash('Lütfen ismi 200 karakterden küçük olacak şekilde giriniz')
            return redirect(url_for('admin.add_member'))
        # Form verileri geçerli mi kontrol ediliyor

        if not file:
            flash('Lütfen bir görsel yükleyin!')
            return redirect(url_for('admin.add_project'))
        # Görsel yüklenmediyse kullanıcı yönlendiriliyor

        member = TeamMember(name=name,
                            designation=designation,
                            fb_link=fb_link,
                            t_link=t_link,
                            i_link=i_link)
        
        member.save()
        # Database'e kaydediliyor

        file.save(f'website/custom_img/team/{member.id}/member.{get_extension(file.filename)}')
        # Görsel kaydediliyor

        return redirect(url_for('views.team'))
        

@admin.route('edit-member/<pk>', methods=['POST', 'GET'])
def edit_member(pk):
    """
    Get ve Post methodu kullanılıyor.
    üye düzenleme
    """
    member = TeamMember.get_or_none(TeamMember.id==pk)
    # Database'den veri çekiliyor

    if not member:
        flash('Üye bulunamadı!')
        return redirect(url_for('admin.panel'))
    # Veri geçerli mi kontrol ediliyor

    if request.method == 'GET':
        return render_template('admin/edit_member.html', member=member)
    else:
        name = request.form.get('name')
        designation = request.form.get('designation')

        fb_link = request.form.get('fb-link')
        t_link = request.form.get('t-link')
        i_link = request.form.get('i-link')
        file = request.files['image']
        # Form verileri alınıyor

        if len(name) > 200:
            flash('Lütfen ismi 200 karakterden küçük olacak şekilde giriniz')
            return redirect(url_for('admin.add_member'))
        # Form verileri kontrol ediliyor

        if file:
            old_image_path = get_image_path('team', pk)
            remove('website/'+old_image_path)

            file.save(f'website/custom_img/team/{member.id}/member.{get_extension(file.filename)}')
        # Eski görsel silip yeni görsel kaydediliyor

        member.name = name
        member.designation = designation

        member.fb_link = fb_link
        member.t_link = t_link
        member.i_link = i_link

        member.save()
        # Değişiklikler kaydediliyor

        return redirect(url_for('views.team'))


@admin.route('delete-member/<pk>')
def delete_member(pk):
    """
    üye silme
    """
    member = TeamMember.get_or_none(TeamMember.id == pk)
    # Üyeyi database'den alıyor

    if not member:
        flash('Üye bulunamadı!')
        return redirect(url_for('admin.panel'))
    # Üye geçerli mi kontrol ediliyor
    
    rmtree(f'website/custom_img/team/{member.id}')
    member.delete_instance()
    # Üyenin görselleri ve database bilgileri siliniyor

    flash('Başarıyla silindi')
    return redirect(url_for('views.team'))

@admin.route('add-testimonial/', methods=['POST', 'GET'])
def add_testimonial():
    """
    Get ve Post Methodu kullanılıyor
    Referans ekleme
    """
    if request.method == 'GET':
        return render_template('admin/add_testimonial.html')
    else:
        client_name = request.form.get('client-name')
        comment = request.form.get('comment')
        profession = request.form.get('profession')

        file = request.files['image']
        # Form verileri değişkenlere kaydediliyor

        if len(client_name) > 100 or len(comment) > 200 or len(profession) > 50:
            flash('Lütfen verileri çok uzun girmeyin!')
            return redirect(url_for('admin.add_testimonial'))
        # Form verileri kontrol ediliyor

        if not file:
            flash('Lütfen bir görsel yükleyin!')
            return redirect(url_for('admin.add_testimonial'))
        # Görsel kontrol ediliyor

        testimonial = Testimonial(client_name=client_name,
                                  comment=comment,
                                  profession=profession)
        
        testimonial.save()
        # Referans database'e kaydediliyor

        file.save(f'website/custom_img/testimonial/{testimonial.id}/testimonial.{get_extension(file.filename)}')
        # Görsel kaydediliyor

        return redirect(url_for('views.testimonial'))

@admin.route('edit_testimoinal/<pk>', methods=['POST', 'GET'])
def edit_testimonial(pk):
    """
    Get ve Post methodu kullanı
    Referans düzenleme
    """
    testimonial = Testimonial.get_or_none(Testimonial.id == pk)
    # Database'den referansı alıyor

    if not testimonial:
        flash('Referans bulunamadı!')
        return redirect(url_for('admin.panel'))
    # Veriyi kontrol ediyor

    if request.method == 'GET':
        return render_template('admin/edit_testimonial.html', testimonial=testimonial)
    
    else:
        client_name = request.form.get('client-name')
        comment = request.form.get('comment')
        profession = request.form.get('profession')

        file = request.files['image']
        # Form verilerini değişkene aktarıyor

        if len(client_name) > 100 or len(comment) > 200 or len(profession) > 50:
            flash('Lütfen verileri çok uzun girmeyin!')
            return redirect(url_for('admin.add_testimonial'))
        # Form verilerinin şartlara uyup uymadığını kontrol ediyor.

        if file:
            old_image_path = get_image_path('testimonial', pk)
            remove('website/'+old_image_path)

            file.save(f'website/custom_img/testimonial/{testimonial.id}/testimonial.{get_extension(file.filename)}')
        # Eski görseli silip yenisini yüklüyor

        testimonial.client_name = client_name
        testimonial.comment = comment
        testimonial.profession = profession

        testimonial.save()
        # Değişiklikleri kaydediyor

        return redirect(url_for('views.testimonial'))

@admin.route('delete_testimonial/<pk>')
def delete_testimonial(pk):
    """
    Referans silme
    """
    testimonial = Testimonial.get_or_none(Testimonial.id == pk)
    # Referansı database'den alıyor

    if not testimonial:
        flash('Referans bulunamadı!')
        return redirect(url_for('admin.panel'))
    # Referansı kontrol ediyor
 
    rmtree(f'website/custom_img/testimonial/{testimonial.id}')
    testimonial.delete_instance()
    # Görsel dosyalarını ve database bilgilerini siliyor

    flash('Başarıyla silindi')
    return redirect(url_for('views.testimonial'))

@admin.route('view_quote/<pk>')
def view_quote(pk):
    """
    Teklif görüntüleme
    """
    quote = Quote.get_or_none(Quote.id==pk)
    # Teklifi database'den alıyor

    if not quote:
        flash('Teklif bulunamadı')
        return redirect(url_for('admin.panel'))
    # Eğer veri yoksa uyarı veriyor

    return render_template('admin/view_quote.html', quote=quote)

@admin.route('delete_quote/<pk>')
def delete_quote(pk):
    """
    Teklif silme
    """
    quote = Quote.get_or_none(Quote.id==pk)
    # Teklifi database'den alıyor

    if not quote:
        flash('Teklif bulunamadı')
        return redirect(url_for('admin.panel'))
    # Eğer teklif yoksa uyarıyor

    quote.delete_instance()
    # Teklifi database'den siliyor

    flash('Başarıyla silindi!')
    return redirect(url_for('admin.panel'))

@admin.route('send-mail', methods=['POST'])
def send_mail():
    """
    Sadece Post methodu kullanıyor
    Üye olanlara mail gönderme
    """
    subject = request.form.get('subject')
    content = request.form.get('ckeditor')
    # form verilerini değişkene kaydediyor

    subscribers = Subscriber.select()
    # Bütün üyeleri seçiyorum

    content = render_template('mail_format.html', title=subject, content=content)
    # Maili tek bir formatta renderlıyor

    Thread(target= lambda: send_email_subscribers(subscribers, subject, content)).start()
    # Asenkron bir şekilde mail gönderme işlemini başlatıyor

    flash('Mail gönderme işlemi başlamıştır!')
    return redirect(url_for('admin.panel'))