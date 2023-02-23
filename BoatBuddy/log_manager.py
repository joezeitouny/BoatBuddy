import logging
from enum import Enum
from logging.handlers import RotatingFileHandler

from events import Events

from BoatBuddy import globals


class LogType(Enum):
    DEBUG = 'debug'
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'


class LogEvents(Events):
    __events__ = ('on_log',)


class LogManager:

    def __init__(self, options):
        self._options = options
        self._events = None
        self._log_filename = ''

        if self._options.log_module:
            # Initialize the logging module
            if not self._options.output_path.endswith('/'):
                self._log_filename = options.output_path + '/' + globals.LOG_FILENAME
            else:
                self._log_filename = options.output_path + globals.LOG_FILENAME

            formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
            # Limit log file size
            file_handler = RotatingFileHandler(self._log_filename, encoding='utf-8', maxBytes=globals.LOG_FILE_SIZE,
                                               backupCount=0)
            file_handler.setFormatter(formatter)

            log_numeric_level = getattr(logging, self._options.log_level.upper(), None)
            logging.getLogger(globals.LOGGER_NAME).setLevel(log_numeric_level)
            logging.getLogger(globals.LOGGER_NAME).addHandler(file_handler)
        else:
            logging.getLogger(globals.LOGGER_NAME).disabled = True

    def debug(self, message):
        if self._options.log_module:
            logging.getLogger(globals.LOGGER_NAME).debug(message)
            if self._events and logging.getLogger(globals.LOGGER_NAME).level <= 10:
                self._events.on_log(LogType.DEBUG, message)

    def info(self, message):
        if self._options.log_module:
            logging.getLogger(globals.LOGGER_NAME).info(message)
            if self._events and logging.getLogger(globals.LOGGER_NAME).level <= 20:
                self._events.on_log(LogType.INFO, message)

    def warning(self, message):
        if self._options.log_module:
            logging.getLogger(globals.LOGGER_NAME).warning(message)
            if self._events and logging.getLogger(globals.LOGGER_NAME).level <= 30:
                self._events.on_log(LogType.WARNING, message)

    def error(self, message):
        if self._options.log_module:
            logging.getLogger(globals.LOGGER_NAME).error(message)
            if self._events and logging.getLogger(globals.LOGGER_NAME).level <= 40:
                self._events.on_log(LogType.ERROR, message)

    def register_for_events(self, events):
        self._events = events

    def get_last_log_entries(self, count) -> []:
        lines = []

        try:
            with open(self._log_filename) as file:
                # loop to read iterate
                # last n lines and print it
                for line in (file.readlines()[-count:]):
                    lines.append(line.rstrip('\r\n'))
        except Exception as e:
            self.error(f'Could not open log file with filename {self._log_filename}. Details: {e}')

        return lines
