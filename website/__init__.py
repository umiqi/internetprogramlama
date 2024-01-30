from flask import Flask, render_template
from flask_ckeditor import CKEditor

def create_app():
    """
    Flask app'i oluşturup döndürür
    """
    from .views import views
    from .admin import admin
    from .auth import auth
    from .lib import lib
    from .static_img import static_img
    from .custom_img import custom_img
    # Blueprint'leri import ediyor

    from .func import get_contact_info, get_few_services
    # Bir kaç adet özel fonksiyonu import ediyor

    app = Flask(__name__)
    ckeditor = CKEditor()
    """ 
    CKEditor nesnesi oluşturuyorum. Bu benim kendi web sitem üzerinde
    kullanıcı için kolay ve kullanışlı bir html editor oluşturmamı sağlıyor. 
    """ 

    app.secret_key = "5aQyDZGu1R6kVSBSM9zg2b2r2P3R1wn4mWPcHaUVlTiF1xjv6M"

    ckeditor.init_app(app)
    # Oluşturduğum neseneyi flask uygulamam için tanımlıyorum

    app.jinja_env.globals.update(get_contact_info=get_contact_info, get_few_services=get_few_services)
    """
     Bu kod sayesinde her seferinde `get_contact_info` ve `get_few_services`
     fonksiyonlarını direkt olarak jinja templatelerine import ediyor bu sayede
     bütün templateler için ayrı ayrı bu fonkisyonları tanımlamamıza gerek kalmıyor.
    """

    @app.errorhandler(404)
    def not_found(e):
        """
        404 hata kodu alındığı takdirde yönlendirilecek sayfa
        """
        return render_template('404.html')

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='')
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(lib, url_prefix='/lib')
    app.register_blueprint(static_img, url_prefix='/img')
    app.register_blueprint(custom_img, url_prefix='/custom-img')
    # Blueprintler import ediliyor...

    return app