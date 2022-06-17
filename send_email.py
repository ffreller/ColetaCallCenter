import email
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from src.helper_functions import get_processed_excel_fpath
from src.definitions import LOGGING_CONFIG
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
    
    
def send_standard_mail(test=False):
    import logging
    import logging.config
    logger = logging.getLogger('standard')
    email_destinations = ['ffreller', 'dagsilva', 'elisa.habiro', 'lcamargo', 'priscilla.duarte']
    if test:
        email_destinations = email_destinations[:1]
    fpath = get_processed_excel_fpath()
    dates = str(fpath).split('Atendimentos_')[1].split('.xlsx')[0].split('_')
    dates = [date.replace('-', '/') for date in dates]
    email_subject =f"Planilha CallCenter {dates[0]} - {dates[1]}"
    email_destinations = [item+"@haoc.com.br" if not item.endswith("@haoc.com.br") else item for item in email_destinations]
    email_sender = "relatorios.tasy@haoc.com.br"
    email_text = f"""Caro(a) colaborador(a),
    
                    Segue anexa a planilha para a semana do dia {dates[0]} até o dia {dates[1]}.

                    Atenciosamente,
                    Equipe Datalab.

                    (Obs: Essa é uma mensagem automática. Para esclarecimentos ou dúvidas, enviar email para datalab@haoc.com.br)"""
    first_break = ",\n    \n"
    tabs = email_text[email_text.find(first_break)+len(first_break): email_text.find('Segue')]
    email_text = email_text.replace(tabs, '')
    send_mail(send_from = email_sender, send_to=email_destinations,
              subject=email_subject, text=email_text,
              server=SMTP_SERVER, port=SMTP_PORT,
              files=[fpath])
    logger.debug('Email enviado com sucesso!')


if __name__ == '__main__':
    send_standard_mail(test=True)