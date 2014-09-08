class NotAllowedError(Exception):
    def __init__(self):
        self.code = 405


class NotFoundError(Exception):
    def __init__(self):
        self.code = 404


