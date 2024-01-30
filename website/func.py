from .models import Services

from json import load
from os import listdir

from pathlib import Path

get_contact_info = lambda: load(open('website/contact.json', encoding='utf-8'))
"""
`contact.json` dosyasını tek fonksiyon ile dict olarak alma
"""
get_about_info = lambda: load(open('website/about.json', encoding='utf-8'))
"""
`about.json` dosyasını tek fonksiyon ile dict olarak alma
"""

get_image_path = lambda folder, pk: f"custom_img/{folder}/{pk}/{listdir(f'website/custom_img/{folder}/{pk}/')[0]}"
"""
Fotoğraf dosyasının yolunu custom_img üzerinden primary key ile alıyor. 
"""

get_few_services = lambda: Services.select().order_by(Services.id.desc()).limit(5)
"""
En alttaki footer için servisleri çekiyor.
"""

get_extension = lambda filename: Path(filename).suffix.replace('.', '')
"""
Dosyaların uzantısını döndürür
"""