from os import system as sys

import smtplib
import imaplib
import email
from email.message import EmailMessage
from email.header import decode_header

conversation = []

class EmailClient:
  def __init__(self, email_address, password, smtp_server, imap_server):
    self.email_address = email_address
    self.password = password
    self.smtp_server = smtp_server
    self.imap_server = imap_server

  def send_email(self, subject, body, to_email):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = self.email_address
    msg['To'] = to_email

    with smtplib.SMTP_SSL(self.smtp_server, 465) as smtp:
      smtp.login(self.email_address, self.password)
      smtp.send_message(msg)

  def receive_emails(self):
    mail = imaplib.IMAP4_SSL(self.imap_server)
    mail.login(self.email_address, self.password)
    mail.select('inbox')

    status, messages = mail.search(None, 'FROM', recipient)
    messages = messages[0].split()
    length = len(messages)
    currently_working_on = 0

    for currently_working_on, mail_id in enumerate(messages, start=1):
        sys('clear')
        print(f'Loading Messages [{currently_working_on}/{length}]')
        _, msg = mail.fetch(mail_id, '(RFC822)')
        for response_part in msg:
            if isinstance(response_part, tuple):
                email_message = email.message_from_bytes(response_part[1])
                subject, _ = decode_header(email_message['Subject'])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(errors='replace')
                if subject == 'CODE[BRANDONBAEK MESSAGING SERVICE] DELETING ASAP':
                    if email_message.is_multipart():
                        for part in email_message.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get('Content-Disposition'))
                            try:
                                body = part.get_payload(decode=True)
                                if body is not None:
                                    body = body.decode(errors='replace').removesuffix('\r\n')
                                    if content_type == 'text/plain' and 'attachment' not in content_disposition:
                                        conversation.append(f'{recipient}: {body}')
                            except:
                                pass
                    else:
                        body = email_message.get_payload(decode=True)
                        if body is not None:
                            body = body.decode(errors='replace').removesuffix('\r\n')
                            conversation.append(f'{recipient}: {body}')
        sys('clear')

  def delete_email(self, subject):
    mail = imaplib.IMAP4_SSL(self.imap_server)
    mail.login(self.email_address, self.password)
    mail.select('inbox')

    status, messages = mail.search(None, 'FROM', recipient)
    messages = messages[0].split()

    for mail_id in messages:
        _, msg = mail.fetch(mail_id, '(RFC822)')
        for response_part in msg:
            if isinstance(response_part, tuple):
                email_message = email.message_from_bytes(response_part[1])
                msg_subject, _ = decode_header(email_message['Subject'])[0]
                if isinstance(msg_subject, bytes):
                    msg_subject = msg_subject.decode(errors='replace')
                if msg_subject == subject:
                    mail.store(mail_id, '+FLAGS', '\\Deleted')
    mail.expunge()


pre_email_data = open("email_data.txt").read().split('\n')
email_data = {}
for data in pre_email_data:
  data_split = data.split()
  password = data_split[1]
  while '_' in password:
    password = password.replace('_', ' ')
  email_data[data_split[0]] = password

email_client_data = []
if input('Do you have an account? (y/n) ').lower() == 'y':
  sys('clear')
  user_email = input('What is your email? ')
  while user_email not in email_data:
    print('Invalid Email')
    user_email = input('What is your email? ')
  sys('clear')

  email_client_data.append(user_email)
  email_client_data.append(email_data[user_email])
else:
  sys('clear')
  user_email = input('What is your email? ')
  password = input('App password? ')

  email_client_data.append(user_email)
  email_client_data.append(password)

  while ' ' in password:
    password = password.replace(' ', '_')
  text_data = open("email_data.txt", "w")
  text_data.write(f'\n{user_email} {password}')
  text_data.close()

email_client = EmailClient(email_client_data[0],
               email_client_data[1],
               'smtp.gmail.com',
               'imap.gmail.com')

recipient = input('Who do you want to text? (Email) ')

email_client.receive_emails()
while True:
  sys('clear')
  for i in conversation:
    print(i)
  email_client.delete_email('CODE[BRANDONBAEK MESSAGING SERVICE] DELETING ASAP')
  user_message = input('\nMessage (Enter nothing to refresh): ')
  if user_message:
    email_client.send_email('CODE[BRANDONBAEK MESSAGING SERVICE] DELETING ASAP', user_message, recipient)
    email_client.receive_emails()
    conversation.append(f'{user_email}: {user_message}')
  else:
      email_client.receive_emails()