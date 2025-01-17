import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

def send_email(receivers, message, subject, paths_to_attachments=[], sender="glj523@dandyweb01fl.unicph.domain"):
    # Set up the MIME message
    msg = MIMEMultipart()
    msg['From'] = sender
    if type(receivers) == list:
        msg['To'] = ", ".join(receivers)
    elif type(receivers) == str:
        msg['To'] = receivers
    else:
        raise Exception('Only list or string input allowed for receivers')
    msg['Subject'] = subject

    # Attach the message body
    msg.attach(MIMEText(message, 'plain'))

    # Attach files if provided
    if len(paths_to_attachments) > 0:
        for attachment_path in paths_to_attachments:
            try:
                with open(attachment_path, "rb") as file:
                    # Create a MIMEBase object to represent the file
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(file.read())
                    encoders.encode_base64(part)  # Encode the file as base64
                    base_name = os.path.basename(attachment_path)
                    # Add file headers
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{attachment_path}"'
                    )
                    
                    # Attach the file to the message
                    msg.attach(part)
            except Exception as e:
                print(f"Could not attach file {attachment_path}: {e}")

    # Set up the SMTP server and send the email
    try:
        with smtplib.SMTP("localhost", 25) as server:
            # Omit server.login() if the server doesn't support or require authentication
            text = msg.as_string()
            server.sendmail(sender, receivers, text)
            print(f"Email successfully sent to {', '.join(receivers)}")
    except Exception as e:
        print(f"Failed to send email: {e}")
