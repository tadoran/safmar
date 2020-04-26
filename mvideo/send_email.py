import os
import smtplib
from datetime import date
from email.headerregistry import Address
from email.message import EmailMessage
from email.utils import make_msgid

import filetype


def send_email_msg(subject,
                   to=[Address("MVideo-parser", "gorelovkg", "yandex.ru")],
                   sender=Address("MVideo-parser", "gorelovkg", "yandex.ru"),
                   html_body="",
                   txt_body="",
                   attachments=[]):
    email_login = os.environ.get('email_login')
    email_password = os.environ.get('email_password')

    if not email_login or not email_password:
        print("Something is wrong!")
        raise EnvironmentError("Email parameters are not set!")

    HOST = "smtp.yandex.ru"
    PORT = 465

    # Create the base text message.
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to

    if txt_body != "":
        msg.set_content(txt_template)
    if html_body != "":
        msg.add_alternative(html_template, subtype='html')

    for att in attachments:

        filename = att.split(os.path.sep)[-1]
        mime_type = filetype.guess(att)
        if mime_type is None:
            maintype, subtype = 'application', 'octet-stream'
        else:
            maintype, subtype = mime_type.MIME.split('/', 1)

        attachment_cid = make_msgid()

        with open(att, 'rb') as att:
            msg.get_payload()[1].add_related(
                att.read(),
                maintype=maintype,
                subtype=subtype,
                cid=attachment_cid,
                filename=filename
            )

    server = smtplib.SMTP_SSL(host=HOST, port=PORT, timeout=10)
    try:
        server.login(email_login, email_password)
        server.send_message(msg)
    finally:
        server.quit()


if __name__ == "__main__":
    parsing_date = date.today()
    date_str = parsing_date.strftime("%d.%m.%Y")

    # att_folder = "C:\\Users\\Gorelov\\Desktop\\tmp"
    att_folder = "./output/"
    _, _, filenames = next(os.walk(att_folder), (None, None, []))
    attachments = [att_folder + "\\" + filename for filename in filenames]

    with open("./templates/mail.html", "r", encoding='utf') as f:
        html_template = f.read()

    with open("./templates/mail.txt", "r", encoding='utf') as f:
        txt_template = f.read()

    replacement_dic = ({
        "{{ today }}": date_str
    })
    for old, new in replacement_dic.items():
        html_template = html_template.replace(old, new)
        txt_template = txt_template.replace(old, new)

    send_email_msg(
        subject=f"М.Видео - цены и акции на {date_str}",
        to=([
            Address("Konstantin Gorelov", "gorelovkg", "yandex.ru"),
            # Address("Konstantin Gorelov", "Konstantin.Gorelov", "bshg.com"),
        ]),
        html_body=html_template,
        txt_body=txt_template,
        attachments=attachments
    )
    print("Done.")
