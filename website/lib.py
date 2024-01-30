from flask import Blueprint, send_from_directory

lib = Blueprint('lib', __name__, static_folder='lib')

@lib.route('/<path:filename>')  
def libraries(filename):  
    """
    template için lib klasörünün içindeki verileri döndürür
    """
    return send_from_directory(lib.static_folder, filename)
