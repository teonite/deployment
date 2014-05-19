__author__ = 'kkrzysztofik'

import os
import smtplib

from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

from deployment.common import pretty_print


def send_mail(send_from, send_to, subject, text, files=[], host="localhost", user="", password="", port=25):
    assert type(send_to) == list
    assert type(files) == list

    pretty_print('Preparing message')
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text))
    pretty_print('Message prepared')

    pretty_print('Preparing files')
    for f in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(f, "rb").read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
        msg.attach(part)

    smtp = smtplib.SMTP(host=host, port=port)

    if len(user):
        smtp.starttls()
        smtp.login(user, password)

    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()