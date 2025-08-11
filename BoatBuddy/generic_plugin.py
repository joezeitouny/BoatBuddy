import time
from enum import Enum
from threading import Thread, Event

from BoatBuddy.log_manager import LogManager
from BoatBuddy.notifications_manager import NotificationsManager
from BoatBuddy import globals


class PluginStatus(Enum):
    STARTING = 'starting'
    RUNNING = 'running'
    DOWN = 'down'


class GenericPlugin:
    _options = None

    def __init__(self, options, log_manager: LogManager, notifications_manager: NotificationsManager):
        self._options = options
        self._log_manager = log_manager
        self._notifications_manager = notifications_manager
        self._log_entries = []
        self._plugin_status = PluginStatus.DOWN
        self._exit_signal = Event()
        self._plugin_thread = Thread(target=self._validate_rules_loop)
        self._plugin_thread.start()

    def get_metadata_headers(self):
        return []

    # Collect all current data in an object in memory (add that object to a list instance if needed)
    def take_snapshot(self, store_entry):
        raise NotImplementedError("Method needs to be implemented")

    def get_metadata_values(self):
        return []

    def get_summary_headers(self):
        return []

    def get_summary_values(self):
        return []

    def clear_entries(self):
        self._log_entries = []

    # Close active sessions (if any), this method is called when a KeyboardInterrupt signal is raised
    def finalize(self):
        raise NotImplementedError("Method needs to be implemented")

    def register_for_events(self, events):
        pass

    def get_status(self) -> PluginStatus:
        raise NotImplementedError("Method needs to be implemented")

    def validate_rules(self):
        raise NotImplementedError("Method needs to be implemented")

    def _validate_rules_loop(self):
        while not self._exit_signal.is_set():
            if self.get_status() == PluginStatus.RUNNING:
                self.validate_rules()

            # sleep a bit
            time.sleep(globals.PLUGIN_VALIDATE_RULES_INTERVAL)