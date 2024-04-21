from enum import Enum
from threading import Thread, Event
import time
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from BoatBuddy.log_manager import LogManager
from BoatBuddy import globals


class EmailManagerStatus(Enum):
    STARTING = 1
    RUNNING = 2
    DOWN = 3


class EmailManager:
    def __init__(self, options, log_manager: LogManager):
        self._options = options
        self._log_manager = log_manager
        self._exit_signal = Event()
        self._email_queue = []
        self._status = EmailManagerStatus.STARTING

        if self._options.email_module:
            self._email_thread = Thread(target=self._main_loop)
            self._email_thread.start()
            self._log_manager.info('Email module successfully started!')

    def send_email(self, subject, body, attachments=None):
        if not self._options.email_module:
            return

        self._email_queue.append({'subject': subject, 'body': body, 'attachments': attachments})

    def finalize(self):
        if not self._options.email_module:
            return

        self._exit_signal.set()
        if self._email_thread:
            self._email_thread.join()

        self._status = EmailManagerStatus.DOWN
        self._log_manager.info('Email manager instance is ready to be destroyed')

    def _main_loop(self):
        while not self._exit_signal.is_set():
            if len(self._email_queue):
                email_entry = self._email_queue[0]

                try:
                    # receiver = self._options.email_receiver_address
                    subject = email_entry['subject']

                    # Create a message object
                    message = MIMEMultipart()
                    message["From"] = f"{globals.APPLICATION_NAME} <{self._options.email_smtp_username}>"
                    message["To"] = self._options.email_address
                    message["Subject"] = subject

                    # Email body
                    body = email_entry['body']
                    message.attach(MIMEText(body, "plain"))

                    # Add attachments if any
                    if not email_entry['attachments'] is None and len(email_entry['attachments']) > 0:
                        for filename in email_entry['attachments']:
                            # Attach file
                            with open(filename, "rb") as attachment:
                                part = MIMEBase("application", "octet-stream")
                                part.set_payload(attachment.read())
                                encoders.encode_base64(part)
                                part.add_header(
                                    "Content-Disposition",
                                    f"attachment; filename= {os.path.basename(filename)}",
                                )
                                message.attach(part)

                    # Connect to the SMTP server
                    with smtplib.SMTP_SSL(host=self._options.email_smtp_server,
                                          port=self._options.email_smtp_port) as server:
                        server.login(self._options.email_smtp_username, self._options.email_smtp_password)
                        # Send email
                        server.sendmail(self._options.email_smtp_username, self._options.email_address,
                                        message.as_string())

                    self._email_queue.pop(0)
                    self._log_manager.info(
                        f'Email successfully sent to {self._options.email_receiver_address} with subject \'{subject}\'!')

                    if self._status != EmailManagerStatus.RUNNING:
                        self._status = EmailManagerStatus.RUNNING
                except Exception as e:
                    if self._status != EmailManagerStatus.DOWN:
                        self._log_manager.info(f'Could not send email. Details {e}')

                        self._status = EmailManagerStatus.DOWN

            time.sleep(1)  # Sleep for one second
