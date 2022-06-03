import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from src.helper_functions import print_with_time, get_excel_fpath
from credentials import SMTP_SERVER, SMTP_PORT


def send_mail(send_from, send_to, subject, text, server, port, files=None):
    assert isinstance(send_to, list)

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    for f in files or []:
        with open(f, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=basename(f)
            )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
        msg.attach(part)


    smtp = smtplib.SMTP(server, port=port)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()
    
    
def send_standard_mail(email_destinations):
    fpath = get_excel_fpath()
    dates = str(fpath).split('processed/')[1].split('_callcenter')[0].split('_')
    email_subject =f"Planilha CallCenter {dates[0]} - {dates[1]}"
    email_destinations = [item+"@haoc.com.br" if not item.endswith("@haoc.com.br") else item for item in email_destinations]
    email_sender = "relatorios.tasy@haoc.com.br"
    email_text = f"""Caro(a) colaborador(a),
    
                    Seguem anexas as planilhas de Sepse das unidades Paulista e Vergueiro para o semana do dia {dates[0]} até o dia {dates[1]}.

                    Atenciosamente,
                    Equipe Datalab.

                    (Obs: Essa é uma mensagem automática. Para esclarecimentos ou dúvidas, enviar email para datalab@haoc.com.br)"""
    first_break = ",\n    \n"
    tabs = email_text[email_text.find(first_break)+len(first_break): email_text.find('Seguem')]
    email_text = email_text.replace(tabs, '')
    send_mail(send_from = email_sender, send_to=email_destinations,
              subject=email_subject, text=email_text,
              server=SMTP_SERVER, port=SMTP_PORT,
              files=[fpath])
    print_with_time('Email enviado com sucesso!')


def send_standard_mail_test():
    email_destinations = ['ffreller']
    print_with_time(f"Enviando email (teste) para: {', '.join(email_destinations)}")
    send_standard_mail(email_destinations) 
 
    
def send_standard_mail_prod():
    email_destinations = ['ffreller',
                          'dagsilva',
                          'elisa.habiro'
                          ]
    print_with_time(f"Enviando email (prod) para: {', '.join(email_destinations)}")
    send_standard_mail(email_destinations)


if __name__ == '__main__':
    send_standard_mail_test()