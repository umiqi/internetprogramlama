import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from json import load

host = "smtp.zoho.eu"
port = 587
email = "umitaltinoz@zohomail.eu "
password = "1598753+0a"
mail_to = load(open('website/mail_adress.json', encoding='utf-8'))

def send_email(subject, template, mail_to=mail_to):
    smtp = smtplib.SMTP(host, port=port) # SMTP nesnesi oluşturuyorum
    smtp.ehlo()
    smtp.starttls() # Server ile TLS kullanrak iletişim kuracağımı söylüyorum
    smtp.login(email, password) # Giriş Yapıyorum

    msg = MIMEMultipart()
    msg['Subject'] = subject # Konuyu ekliyorum
    msg.attach(MIMEText(template, 'html')) # Html sayfasını render edip html biçiminde olduğunu söylüyorum

    smtp.sendmail(email, mail_to, msg.as_string())# Maili gönderiyorum
    smtp.quit()

def send_email_subscribers(subscribers, subject, template):
    smtp = smtplib.SMTP(host, port=port) # SMTP nesnesi oluşturuyorum
    smtp.ehlo()
    smtp.starttls() # Server ile TLS kullanrak iletişim kuracağımı söylüyorum
    smtp.login(email, password) # Giriş Yapıyorum

    msg = MIMEMultipart()
    msg['Subject'] = subject # Konuyu ekliyorum
    msg.attach(MIMEText(template, 'html')) # Html sayfasını render edip html biçiminde olduğunu söylüyorum

    for subscriber in subscribers:
        try:
            smtp.sendmail(email, subscriber.email, msg.as_string()) # Maili gönderiyorum
        except Exception as error:
            print(error)
    smtp.quit()
