import time


class Log:
    log_entries = []

    def __init__(self, utc_time, local_time, filename_prefix):
        self.utc_time = utc_time
        self.local_time = local_time
        suffix = time.strftime("%Y%m%d%H%M%S", utc_time)
        self.name = f'{filename_prefix}{suffix}'

    def get_utc_time(self):
        return self.utc_time

    def get_name(self):
        return self.name

    def add_entry(self, entry):
        if entry is not None:
            self.log_entries.append(entry)

    def get_entries(self):
        return self.log_entries
