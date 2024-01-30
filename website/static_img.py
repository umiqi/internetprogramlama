from flask import Blueprint, send_from_directory

static_img = Blueprint('static_img', __name__, static_folder='static_img')

@static_img.route('/<path:filename>')
def static_images(filename):
    """
    template için static_img klasörünün içindeki verileri döndürür
    """
    return send_from_directory(static_img.static_folder, filename)