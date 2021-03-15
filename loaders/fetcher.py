class Fetcher:
    def __init__(self):
        self.data = {}  # A dictionary of dataframes indexed by name of table

    def load_data(self):
        raise NotImplementedError('Fetcher is an abstract class, it cannot be used directly!')

    def get_data(self):
        return self.data

    def close(self):
        raise NotImplementedError('Fetcher is an abstract class, it cannot be used directly!')

