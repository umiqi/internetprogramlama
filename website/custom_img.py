from flask import Blueprint, send_file

from .func import get_image_path

custom_img = Blueprint('custom_img', __name__)

@custom_img.route('/<img_location>/<pk>')
def img(img_location, pk):
    """
    Kullanıcıların yükledikleri resimlere erişiyor
    """
    try:
        return send_file(get_image_path(img_location, pk))
    except Exception as excep:
        return "<h1>Not Found</h1>", 404
    
