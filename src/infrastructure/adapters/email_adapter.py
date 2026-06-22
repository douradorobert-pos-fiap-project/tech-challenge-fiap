from src.application.ports.external.email_port import EmailPort
from src.infrastructure.config.settings import settings


class SMTPEmailAdapter(EmailPort):
    def __init__(self) -> None:
        self._host = settings.SMTP_HOST
        self._port = settings.SMTP_PORT
        self._user = settings.SMTP_USER
        self._password = settings.SMTP_PASSWORD
        self._from = settings.SMTP_FROM

    def enviar_email(self, destinatario: str, assunto: str, corpo: str) -> None:
        import smtplib
        from email.mime.text import MIMEText

        msg = MIMEText(corpo, "html", "utf-8")
        msg["Subject"] = assunto
        msg["From"] = self._from
        msg["To"] = destinatario

        with smtplib.SMTP(self._host, self._port) as server:
            if self._user and self._password:
                server.starttls()
                server.login(self._user, self._password)
            server.sendmail(self._from, [destinatario], msg.as_string())
