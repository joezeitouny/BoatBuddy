from enum import Enum
from threading import Thread, Event
import asyncio

from telegram import Update, Bot
from telegram.error import Forbidden, NetworkError

from BoatBuddy.log_manager import LogManager
from BoatBuddy import globals


class TelegramManagerStatus(Enum):
    STARTING = 1
    RUNNING = 2
    DOWN = 3


class TelegramManager:
    def __init__(self, options, log_manager: LogManager):
        self._options = options
        self._log_manager = log_manager
        self._exit_signal = Event()
        self._message_queue = []
        self._status = TelegramManagerStatus.STARTING

        if self._options.telegram_module:
            self._recipients = self._options.telegram_recipient_id.split(';')
            self._status = TelegramManagerStatus.RUNNING
            self._log_manager.info('Telegram module successfully started!')
            self.send_message(f"Telegram notifications are successfully enabled on {self._options.boat_name}!\r\n\r\n"
                              f"--\r\n{globals.APPLICATION_NAME} ({globals.APPLICATION_VERSION})")

    def finalize(self):
        if not self._options.email_module:
            return

        self._exit_signal.set()

        self._status = TelegramManagerStatus.DOWN
        self._log_manager.info('Telegram manager instance is ready to be destroyed')

    def send_message(self, message: str):
        if self._options.telegram_module and self._status == TelegramManagerStatus.RUNNING:
            try:
                asyncio.run(self.async_send_message(message))
            except Exception as e:
                self._log_manager.warning(f'Error while sending Telegram notification. Details: {message}')

    async def async_send_message(self, message: str):
        async with Bot(self._options.telegram_bot_token) as bot:
            try:
                for recipient in self._recipients:
                    await bot.send_message(chat_id=recipient, text=message)
                self._log_manager.info(f'Telegram notification with message \'{message}\' successfully sent out!')
            except NetworkError as e:
                await asyncio.sleep(1)
                self._log_manager.warning(f'Error while sending Telegram notification. Details: {message}')
            except Forbidden as e:
                self._log_manager.warning(f'Error while sending Telegram notification. Details: {message}')
            except Exception as e:
                self._log_manager.warning(f'Error while sending Telegram notification. Details: {message}')
