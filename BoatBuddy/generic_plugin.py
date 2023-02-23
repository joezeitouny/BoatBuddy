from enum import Enum

from BoatBuddy.log_manager import LogManager


class PluginStatus(Enum):
    STARTING = 'starting'
    RUNNING = 'running'
    DOWN = 'down'


class GenericPlugin:
    _options = None

    def __init__(self, options, log_manager: LogManager):
        self._options = options
        self._log_manager = log_manager
        self._log_entries = []

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
