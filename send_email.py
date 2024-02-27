import smtplib
import ssl
from email.message import EmailMessage
import os
import constants

def send(subject, body):
    email_sender = constants.EMAIL_SENDER
    # email_password = os.environ.get('EMAIL_PASSWORD')
    email_password = 'hkas tppg gmiq glqw'
    email_receiver = constants.ADMIN_EMAIL

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())

 
