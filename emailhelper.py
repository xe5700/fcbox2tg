from email.mime.text import MIMEText
from smtplib import *
from dataclasses import dataclass
from email.message import EmailMessage

from appcfg import SMTP丰巢推送


class SmtpPush:
    srv: SMTP
    cfg: SMTP丰巢推送

    def __init__(self, app):
        from mainapp import Application
        app: Application
        self.cfg = app.cfg.smtp
        cfg = self.cfg
        if cfg.ssl:
            self.srv = SMTP_SSL(host=cfg.server, port=cfg.port, local_hostname="FCBOXHELPER")
        else:
            self.srv = SMTP(host=cfg.server, port=cfg.port, local_hostname="FCBOXHELPER")
        self.srv.login(cfg.username, cfg.password)

    def send(self, addrs, subject, content):
        cfg = self.cfg
        msg = EmailMessage()
        msg.set_content(content)
        msg["From"] = cfg.sender
        msg["To"] = addrs
        msg["Subject"] = subject

        self.srv.send_message(msg=msg)
