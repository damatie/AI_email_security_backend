# app/services/email_service.py

from smtplib import SMTP, SMTPException
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import HTTPException
from app.core.config import settings
import logging


class EmailService:
    def __init__(self):
        self.from_email = settings.FROM_EMAIL
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.username = settings.EMAIL_USERNAME
        self.password = settings.EMAIL_PASSWORD

    def send_email(self, to_email: str, subject: str, body: str, html_body: str = None):
        """
        Sends an email using SMTP.
        Supports both plain text and HTML content.
        """
        try:
            # Create a MIME message
            msg = MIMEMultipart("alternative")
            msg["From"] = self.from_email
            msg["To"] = to_email
            msg["Subject"] = subject

            # Attach plain text and HTML content
            msg.attach(MIMEText(body, "plain"))
            if html_body:
                msg.attach(MIMEText(html_body, "html"))

            # Connect to SMTP server
            with SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Start encrypted communication
                server.login(self.username, self.password)
                server.sendmail(self.from_email, to_email, msg.as_string())  # Send the email
            logging.info(f"Email sent successfully to {to_email}")

        except SMTPException as e:
            logging.error(f"Failed to send email to {to_email}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Email sending failed. Please try again later.",
            )

    def send_verification_email(self, email: str, token: str):
        """
        Sends an email verification link to the user's email address.
        """
        verification_link = f"http://127.0.0.1:8000/auth/verify_email/{token}"
        subject = "Verify Your Email Address"

        plain_body = f"""
        Hi,

        Please click the following link to verify your email address:
        {verification_link}

        If you did not create this account, please ignore this email.

        Regards,
        Your App Team
        """

        html_body = f"""
        <html>
        <body>
            <p>Hi,</p>
            <p>Please click the following link to verify your email address:</p>
            <a href="{verification_link}">Verify Email Address</a>
            <p>If you did not create this account, please ignore this email.</p>
            <p>Regards,<br>Your App Team</p>
        </body>
        </html>
        """

        self.send_email(email, subject, plain_body, html_body)