#https://realpython.com/python-send-email/
#https://www.brevo.com/
#https://moosend.com/blog/free-smtp-server/
# pip3 install Certificates


import smtplib
import ssl
from email.message import EmailMessage
import os  # To access environment variables
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def send_email(subject, email_body, receiver_email):
    port = 587
    smtp_server = "smtp.gmail.com"
    
    # Retrieve sender's credentials from environment variables
    # This is much safer than hardcoding them
    sender_email = os.environ.get("SENDER_EMAIL")
    password = os.environ.get("SENDER_PASSWORD")

    if not sender_email or not password:
        print("Error: Sender email or password not found in environment variables.")
        return

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.set_content(email_body)

    try:
        # Create a default, secure SSL context
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        with smtplib.SMTP(smtp_server, port, timeout=10) as server:
            server.starttls(context=context)  # Secure the connection
            server.login(sender_email, password)
            # Convert the EmailMessage object to a string before sending
            text_to_send = msg.as_string()
            server.sendmail(sender_email, receiver_email, text_to_send)
            print("Email has been sent successfully...")
    except smtplib.SMTPAuthenticationError:
        print("Authentication failed. Please check your email and app password.")
    except Exception as e:
        print(f"An error occurred: {e}") 



receiver_email = "ravindrakumarmore79@gmail.com"
Subject = "Email Test demo"
message = """\
    This message is sent from Python demo."""

send_email(Subject, message, receiver_email)
