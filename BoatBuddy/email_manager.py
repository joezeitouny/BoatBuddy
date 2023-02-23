from enum import Enum
from threading import Thread, Event

import yagmail

from BoatBuddy.log_manager import LogManager


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
                    receiver = self._options.email_address
                    subject = email_entry['subject']
                    yagmail.register(self._options.email_address, self._options.email_password)
                    yag = yagmail.SMTP(receiver)
                    yag.send(to=receiver, subject=subject, contents=email_entry['body'],
                             attachments=email_entry['attachments'])
                    self._email_queue.pop(0)
                    self._log_manager.info(f'Email successfully sent to {receiver} with subject \'{subject}\'!')

                    if self._status != EmailManagerStatus.RUNNING:
                        self._status = EmailManagerStatus.RUNNING
                except Exception as e:
                    if self._status != EmailManagerStatus.DOWN:
                        self._log_manager.info(f'Could not send email. Details {e}')

                        self._status = EmailManagerStatus.DOWN
