class Plugin:
    metadata_headers = None
    metadata_values = None
    args = None

    def __init__(self, args):
        self.args = args
        self.metadata_headers = []
        self.metadata_values = []

    def get_metadata_headers(self):
        return self.metadata_headers

    def get_metadata_values(self, print_func):
        return self.metadata_values
