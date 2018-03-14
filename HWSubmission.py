import smtplib
import os
import re
import base64
import configparser
import getpass
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders


def send_mail(send_from, send_to, subject, message, files,
              server, port, username, password,
              use_tls=True):
    """Compose and send email with provided info and attachments.

    Args:
        send_from (str): from name
        send_to (str): to name
        subject (str): message title
        message (str): message body
        files (list[str]): list of file paths to be attached to email
        server (str): mail server host name
        port (int): port number
        username (str): server auth username
        password (str): server auth password
        use_tls (bool): use TLS mode
    """
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = send_to
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(message))
    for path in files:
        part = MIMEBase('application', "octet-stream")
        with open(path, 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename="%s"' % os.path.basename(path))
        msg.attach(part)
    try:
        s = smtplib.SMTP()
        s.connect(server)
        s.login(username,password)
        s.sendmail(send_from, [send_to,send_from], msg.as_string())
        s.close()
        return True
    except smtplib.SMTPException as e:
        print(e)

def confirm(text):
    inquiry = input(text)
    if inquiry.lower() in ['y','yes','']:
        return True
    else:
        return False

def is_found(name, root_path):
    for file in os.listdir(root_path):
        if file == name:
            return True
    return False

def main():
    config = configparser.ConfigParser()
    root_path = os.path.dirname(__file__)
    path = os.path.join(root_path, 'config.ini')
    if is_found('config.ini', root_path):
        config.read(path)
        sec = config['DEFAULT']
        s_email = sec['SENDER']
        psw = sec['PSW']
        smtp_server = sec['SERVER']
        smtp_port = sec['PORT']
        t_email = sec['REC']
        subj = sec['SUBJECT']
        mess = sec['MESSAGE']
        direc = sec['DIR']
    else:
        s_email = input('Your email: ')
        psw = getpass.getpass('Your password: ')
        smtp_server = input('SMTP server: ')
        smtp_port = int(input('SMTP server port: '))
        t_email = input('Teacher email: ')
        subj = input('Subject head: ')
        mess = input('Message: ')
        direc = input('Your hw directory: ')
        config['DEFAULT'] = {'SENDER': s_email,
        'PSW': psw,
        'SERVER': smtp_server,
        'PORT': smtp_port,
        'REC': t_email,
        'SUBJECT': subj,
        'MESSAGE': mess,
        'DIR': direc}
        with open(path, 'w') as configfile:
            config.write(configfile)
        print('Configuration saved! To reset, please delete the config.ini file.')
    
    hw_name = input('Name of the homework: ')
    sub = subj + hw_name
    mes = mess
    att = []
    for root, dirs, files in os.walk(direc):
        for file in files:
            if re.search(hw_name, file, re.IGNORECASE):
                att.append(os.path.join(root, file))
    if not att:
        print('Sorry dude, seems like you have not yet done your homework.')
        return
    elif len(att) == 1:
        result = confirm('%s\nIs this the file you want to submit? ' % att[0])
        if result:
            att = att[0]
        else:
            print('Sorry, do it yourself then.')
            return
    else:
        for i in range(len(att)):
            print('[%d] %s' % (i, att[i]))
        ans = int(input('Which file do you want to submit? '))
        att = att[ans]
    rec =  int(input('Do you want to send to [0] Yourself or [1] Teacher? '))
    if rec == 0:
        rec = s_email
    else:
        rec = t_email
    print('Your file is being sent. Please wait.')
    send_mail(send_from=s_email, send_to=rec, subject=sub, message=mes, files=[att],
                server=smtp_server, port=smtp_port, username=s_email, password=psw,
                use_tls=True)
    print('\n*[Your assignment has been submitted to %s]\n    Name: %s\n    File: %s' % (rec, hw_name, att))

if __name__ == "__main__":
    main()