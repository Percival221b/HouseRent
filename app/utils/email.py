import smtplib
from email.message import EmailMessage

from flask import current_app


class MailConfigError(RuntimeError):
    pass


def send_email(to_address: str, subject: str, body: str) -> None:
    if current_app.config.get("MAIL_SUPPRESS_SEND"):
        return

    server = current_app.config.get("MAIL_SERVER")
    port = int(current_app.config.get("MAIL_PORT") or 465)
    username = current_app.config.get("MAIL_USERNAME")
    password = current_app.config.get("MAIL_PASSWORD")
    sender = current_app.config.get("MAIL_DEFAULT_SENDER") or username
    use_ssl = current_app.config.get("MAIL_USE_SSL", True)

    if not server or not username or not password or not sender:
        raise MailConfigError("邮件服务未配置，请检查 MAIL_SERVER、MAIL_USERNAME 和 MAIL_PASSWORD")

    message = EmailMessage()
    message["From"] = sender
    message["To"] = to_address
    message["Subject"] = subject
    message.set_content(body)

    if use_ssl:
        with smtplib.SMTP_SSL(server, port, timeout=15) as smtp:
            smtp.login(username, password)
            smtp.send_message(message)
    else:
        with smtplib.SMTP(server, port, timeout=15) as smtp:
            smtp.starttls()
            smtp.login(username, password)
            smtp.send_message(message)
