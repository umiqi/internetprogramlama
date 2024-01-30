from peewee import SqliteDatabase, Model, CharField, DateField, TextField

from datetime import date
from os import mkdir

"""
Database modellerinin tutulduğu bölüm
"""

db = SqliteDatabase('database.db')

class BaseModel(Model):
    """
    Temel Model
    """
    class Meta:
        database = db

class User(BaseModel):
    """
    Kullanıcı modeli
    """
    username = CharField(max_length=200, unique=True)
    password = CharField(max_length=200)

class Subscriber(BaseModel):
    """
    Üye modeli
    """
    email = CharField(max_length=200)
    subscribed_date = DateField(default=date.today)

class Services(BaseModel):
    """
    Servis modeli
    """
    title = CharField(max_length=200)
    description = CharField(max_length=500)

    def save(self, *args, **kwargs):
        """
        Her kayıt yapıldığında kayıt için bir görsel klasörü oluşturur
        """
        super(Services, self).save(*args, **kwargs)

        try:
            mkdir(f"website/custom_img/services/{self.id}/")
        except FileExistsError:
            pass
        finally:
            return self.id

class Projects(BaseModel):
    """
    Proje Modeli
    """
    title = CharField(max_length=200)
    type = CharField(max_length='100', choices=[('General Carpentry', 'General Carpentry'), ('Custom Carpentry', 'Custom Carpentry')])

    def save(self, *args, **kwargs):
        """
        Her kayıt yapıldığında kayıt için bir görsel klasörü oluşturur
        """
        super(Projects, self).save(*args, **kwargs)

        try:
            mkdir(f"website/custom_img/projects/{self.id}/")
        except FileExistsError:
            pass
        finally:
            return self.id
        
class TeamMember(BaseModel):
    """
    Takım üyesi modeli
    """
    name = CharField(max_length=200)
    designation = CharField()
    fb_link = CharField(null=True)
    i_link = CharField(null=True)
    t_link = CharField(null=True)

    def save(self, *args, **kwargs):
        """
        Her kayıt yapıldığında kayıt için bir görsel klasörü oluşturur
        """
        super(TeamMember, self).save(*args, **kwargs)

        try:
            mkdir(f"website/custom_img/team/{self.id}/")
        except FileExistsError:
            pass
        finally:
            return self.id
        
class Testimonial(BaseModel):
    """
    Referans Modeli
    """
    comment = CharField(max_length=200)
    client_name = CharField(max_length=100)
    profession = CharField(max_length=50)

    def save(self, *args, **kwargs):
        """
        Her kayıt yapıldığında kayıt için bir görsel klasörü oluşturur
        """
        super(Testimonial, self).save(*args, **kwargs)

        try:
            mkdir(f"website/custom_img/testimonial/{self.id}/")
        except FileExistsError:
            pass
        finally:
            return self.id
        
class Quote(BaseModel):
    """
    Teklif modeli
    """
    name = CharField(max_length=100)
    email = CharField(max_length=100)
    mobile = CharField(max_length=50, null=True)
    service = CharField(max_length=200, null=True)
    note = TextField()
