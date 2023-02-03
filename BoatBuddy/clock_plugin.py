import time
from datetime import datetime
from time import mktime

from BoatBuddy import utils
from BoatBuddy.generic_plugin import GenericPlugin


class TimeEntry:
    def __init__(self, utc_time, local_time):
        self._utc_time = utc_time
        self._local_time = local_time

    def __str__(self):
        return utils.get_comma_separated_string(self.get_values())

    def get_values(self):
        return [f'{time.strftime("%Y-%m-%d %H:%M:%S", self._utc_time)}',
                f'{time.strftime("%Y-%m-%d %H:%M:%S", self._local_time)}']

    def get_utc_timestamp(self):
        return self._utc_time

    def get_local_timestamp(self):
        return self._local_time


class TimePlugin(GenericPlugin):
    _log_entries = []

    def __init__(self, args):
        # invoking the __init__ of the parent class
        GenericPlugin.__init__(self, args)

    def get_metadata_headers(self):
        return ["UTC Timestamp", "Local Timestamp"]

    def take_snapshot(self):
        entry = TimeEntry(time.gmtime(), time.localtime())

        # Add it to the list of entries in memory
        self._log_entries.append(entry)

    def get_metadata_values(self):
        # Return last entry values
        return self._log_entries[len(self._log_entries) - 1].get_values()

    def get_summary_headers(self):
        return ["Starting Timestamp (UTC)", "Starting Timestamp (Local)", "Ending Timestamp (UTC)",
                "Ending Timestamp (Local)", "Duration"]

    def get_summary_values(self):
        log_summary_list = []

        if len(self._log_entries) > 0:
            first_entry = self._log_entries[0]
            last_entry = self._log_entries[len(self._log_entries) - 1]

            # Collect timestamps
            log_summary_list.append(f'{time.strftime("%Y-%m-%d %H:%M:%S", first_entry.get_utc_timestamp())}')
            log_summary_list.append(f'{time.strftime("%Y-%m-%d %H:%M:%S", first_entry.get_local_timestamp())}')
            log_summary_list.append(f'{time.strftime("%Y-%m-%d %H:%M:%S", last_entry.get_utc_timestamp())}')
            log_summary_list.append(f'{time.strftime("%Y-%m-%d %H:%M:%S", last_entry.get_local_timestamp())}')

            ending_date = datetime.fromtimestamp(mktime(last_entry.get_utc_timestamp()))
            starting_date = datetime.fromtimestamp(mktime(first_entry.get_utc_timestamp()))
            duration = ending_date - starting_date
            log_summary_list.append(f'{duration}')

        return log_summary_list

    def reset_entries(self):
        self._log_entries = []

    def finalize(self):
        utils.console_out("Time plugin worker terminated")

    def get_last_utc_timestamp_entry(self):
        if len(self._log_entries) > 0:
            return self._log_entries[len(self._log_entries) - 1].get_utc_timestamp()
        else:
            return time.gmtime()