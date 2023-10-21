from enum import Enum
from threading import Thread, Event

from BoatBuddy.log_manager import LogManager
from BoatBuddy.plugin_manager import PluginManager
from BoatBuddy.email_manager import EmailManager


class AnchorManagerStatus(Enum):
    STARTING = 1
    RUNNING = 2
    DOWN = 3


class AnchorManager:
    def __init__(self, options, log_manager: LogManager, plugin_manager: PluginManager, email_manager: EmailManager):
        self._options = options
        self._log_manager = log_manager
        self._plugin_manager = plugin_manager
        self._email_manager = email_manager
        self._exit_signal = Event()

        self._status = AnchorManagerStatus.STARTING
        self._anchor_latitude = ''
        self._anchor_longitude = ''
        self._anchor_allowed_distance = 0
        self._anchor_is_set = False
        self._anchor_alarm_is_active = False
        self._anchor_distance = 0

        if self._options.anchor_alarm_module:
            self._anchor_thread = Thread(target=self._main_loop)
            self._anchor_thread.start()
            self._log_manager.info('Anchor alarm module successfully started!')
        else:
            self._status = AnchorManagerStatus.DOWN

    def finalize(self):
        if not self._options.anchor_alarm_module:
            return

        self._exit_signal.set()
        if self._anchor_thread:
            self._anchor_thread.join()

        self._status = AnchorManagerStatus.DOWN
        self._log_manager.info('Anchor manager instance is ready to be destroyed')

    def set_anchor(self, latitude, longitude, allowed_distance):
        # cancel existing anchor (if any)
        self.cancel_anchor()

        self._anchor_latitude = latitude
        self._anchor_longitude = longitude
        self._anchor_allowed_distance = allowed_distance
        self._anchor_is_set = True

    def cancel_anchor(self):
        self._anchor_is_set = False
        self._anchor_alarm_is_active = False

    def anchor_is_set(self):
        return self._anchor_is_set

    def anchor_latitude(self):
        return self._anchor_latitude

    def anchor_longitude(self):
        return self._anchor_longitude

    def anchor_allowed_distance(self):
        return self._anchor_allowed_distance

    def anchor_alarm_is_active(self):
        return self._anchor_alarm_is_active

    def anchor_distance(self):
        return self._anchor_distance

    def _main_loop(self):
        while not self._exit_signal.is_set():
            try:
                # Retrieve current gps position and calculate distance
                if self._anchor_is_set:
                    continue
            except Exception as e:
                if self._status != AnchorManagerStatus.DOWN:
                    self._log_manager.info(f'Exception occurred in Anchor manager main thread. Details {e}')

                    self._status = AnchorManagerStatus.DOWN

