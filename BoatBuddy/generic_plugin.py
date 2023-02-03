class GenericPlugin:
    _args = None

    def __init__(self, args):
        self._args = args

    def get_metadata_headers(self):
        return []

    # Collect all current data in an object in memory (add that object to a list instance if needed)
    def take_snapshot(self):
        raise NotImplementedError("Method needs to be implemented")

    def get_metadata_values(self):
        return []

    def get_summary_headers(self):
        return []

    def get_summary_values(self):
        return []

    def reset_entries(self):
        raise NotImplementedError("Method needs to be implemented")

    # Close active sessions (if any), this method is called when a KeyboardInterrupt signal is raised
    def finalize(self):
        raise NotImplementedError("Method needs to be implemented")

    def register_for_events(self, events):
        pass
