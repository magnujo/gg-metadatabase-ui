import smtplib
import ssl
from email.message import EmailMessage
import os
import constants.misc_constants as misc_constants

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def send(subject, body, attachment_paths):
    email_sender = misc_constants.EMAIL_SENDER
    email_password = os.environ.get('EMAIL_PASSWORD')
    email_receiver = misc_constants.ADMIN_EMAIL

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    for attachment_path in attachment_paths:
        with open(attachment_path, 'rb') as f:
            file_data = f.read()
            file_name = os.path.basename(attachment_path)
        em.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)
    
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.send_message(em)
        # smtp.sendmail(email_sender, email_receiver, em.as_string())

 
