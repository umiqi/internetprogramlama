from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash

from .models import User
from .decorators import loged_in_required, loged_out_required

auth = Blueprint('auth', __name__)

@auth.route('login', methods=['GET', 'POST'])
@loged_out_required
def login():
    """
    Get ve post methodlarını kullanıyor
    """
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form.get('username').strip().lower()
        password = request.form.get('password')
        # Form verilerini çekiyor

        user = User.get_or_none(User.username == username)
        # Kullanıcıyı database'den çekiyor

        if not user:
            flash('Kullanıcı bulunamadı')
            return redirect(url_for('auth.login'))
        # Kullanıcı eğer yoksa yönlendiriyor

        if check_password_hash(user.password, password):
            """
            Giriş yapan kullanıcıdan aldığı şifreyi sha256 ile şifreliyor
            ve database'deki şifre ile karşılaştırıyor
            """
            session['username'] = username
            session['id'] = user.id
            # Eğer karşılaştırma başarılıysa giriş yapılıyor

            flash('Başarıyla giriş yaptınız')
            return redirect(url_for('admin.panel'))
        else:
            flash('Your password is incorrect')
            return redirect(url_for('auth.login'))
        
@auth.route('logout')
def logout():
    # Çıkış yap
    session.clear()
    return redirect(url_for('views.home'))

@auth.route('change-password', methods=['POST'])
@loged_in_required
def change_password():
    old_password = request.form.get('old-password')
    new_password = request.form.get('new-password')
    password_confirm = request.form.get('password-confirm')
    # Form verilerini kontrol ediyor

    if len(new_password) > 5 and new_password == password_confirm:
        # Kullanıcı şartlara uygun bir şifre girdiyse
        
        user = User.select().where(User.id == session['id']).get()
        # Database'den kullanıcıyı çekiyor

        if check_password_hash(user.password, old_password):
            # Eski şifreyi şifreleyip database'deki ile uyuşup uyuşmadığını kontrol ediyor
            
            user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
            user.save()
            # kontrol başarılıysa yeni şifreyi şifreliyor ve kaydediyor

            flash('Parolanız başarıyla değiştirilmiştir')
            return redirect(url_for('admin.panel'))
        
    elif len(new_password) < 5:
        flash('Password must be greater than 5 chracters')
        return redirect(url_for('auth.login'))
    else:
        flash('Passwords does not match!')
        return redirect(url_for('auth.login'))
    
@auth.route('register-admin', methods=['GET', 'POST'])
def register_admin():
    """
    Get ve Post methodlarını kullanıyor
    Yeni Admin kullanıcısı kayıt olma
    """
    if session['username'] != 'admin':
        flash('Sadece admin kullanıcısı yeni admin kayededebilir!')
        return redirect(url_for('admin.panel'))
    # Kullanıcı kaydeden kişinin admin olup olmadığını kontrol ediyor

    if request.method == 'GET':
        return render_template('admin/register_admin.html')
    else:
        username = request.form.get('username').strip().lower()
        password = request.form.get('password')
        password_re = request.form.get('password-repeat')
        # Form verilerini değişkene aktarıyorum

        if password != password_re:
            flash('Şifreler uyuşmuyor')
            return redirect(url_for('auth.register_admin'))
        # Şifreler uyuşmuyorsa

        if username == 'admin':
            flash('Kullanıcı adınız admin olamaz')
            return redirect(url_for('auth.register_admin'))
        # Kullanıcı adı kontrolü

        user = User(username=username,
                    password=generate_password_hash(password, method='pbkdf2:sha256'))
        user.save()
        # Kullanıcıyı kaydetme

        flash('Başarıyla kaydedildi')
        return redirect(url_for('admin.panel'))