""" Application emails"""
import os
import smtplib
import ssl
import html2text

from flask import render_template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .urls import URLs

class Mail:
    def __init__(self, email_to: str, subject: str, html: str):
        self.email_to = email_to
        self.subject = subject
        self.html = html

class UsernameMail(Mail):
    """Username email."""
    def __init__(self, email_to: str, username: str):
        super().__init__(email_to, "Your account username", 
            render_template("/email/username.html", username=username))

class PasswordResetMail(Mail):
    """Password reset email."""
    def __init__(self, email_to: str, token: str):
        super().__init__(email_to, "Reset your password", 
            render_template("/email/reset_password.html", reset_url=URLs.change_password_url(token)))

class VerifyMail(Mail):
    """Verify email."""
    def __init__(self, email_to: str, token: str):
        super().__init__(email_to, "Please verify your email", 
            render_template("/email/verify_email.html", confirm_url=URLs.verify_email_url(token)))

class OTPMail(Mail):
    """OTP email."""
    def __init__(self, email_to: str, otp: str):
        super().__init__(email_to, "Your one time password", 
            render_template("/email/otp.html", otp=otp))

class UnrecognizedAccessMail(Mail):
    """Unrecognized access email."""
    def __init__(self, email_to: str, details: dict, token: str):
        super().__init__(email_to, "Unrecognized access location.", 
            render_template("/email/unrecognized_access.html", location=details, reset_url=URLs.change_password_url(token)))

class Emails:
    """ Email Service."""
    def __init__(self, app=None):
        if app is not None:
            self.init(app)

    def init(self, app) -> None:
        self.host = app.config["SMPT_HOST"]
        self.port = app.config["SMPT_PORT"]
        self.sender = app.config["SMPT_SENDER"]
        self.sender_pwd = app.config["SMPT_SENDER_PWD"]
        self.sender_from = app.config["SMPT_SENDER_FROM"]            

    def __send_email(self, email_to: str, subject: str, html: str) -> None:
        """Sends a multi-part email."""

        message = MIMEMultipart("alternative")
        message["From"] = self.sender_from
        message["To"] = email_to
        message["Subject"] = subject

        message.attach(MIMEText(html2text.HTML2Text().handle(html), "plain"))
        message.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL(self.host, self.port) as server:
            server.login(self.sender, self.sender_pwd)
            server.sendmail(self.sender, email_to, message.as_string())
        
    def send(self, mail: Mail) -> None:
        self.__send_email(mail.email_to, mail.subject, mail.html)
