import os
import smtplib
from email.message import EmailMessage
import ssl
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

class EmailDetails(BaseModel):
    recipient: str = Field(description="The recipient's email address.")
    subject: str = Field(description="The subject of the email.")
    body: str = Field(description="The complete body of the email.")
    image_url: str = Field(description="Optional URL of an image to embed.", default="")

class SendEmailTool(BaseTool):
    # ... (rest of your tool class definition)

    def _run(self, recipient: str, subject: str, body: str, image_url: str = "") -> str:
        # ... (email credential check)
        
        try:
            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = sender_email
            msg["To"] = recipient

            # Set plain text content
            msg.set_content(body)

            # Add an HTML part if an image URL is provided
            if image_url:
                html_body = f"""
                <html>
                    <body>
                        <p>{body}</p>
                        <img src="{image_url}" alt="Image from Internet" />
                    </body>
                </html>
                """
                msg.add_alternative(html_body, subtype="html")

            # ... (SMTP connection and login)
            
            with smtplib.SMTP(smtp_server, int(smtp_port), timeout=10) as smtp_conn:
                smtp_conn.starttls(context=ssl.create_default_context())
                smtp_conn.login(sender_email, sender_password)
                smtp_conn.send_message(msg)
                
            return "Email sent successfully with image!"
        except Exception as e:
            return f"Failed to send email: {e}"