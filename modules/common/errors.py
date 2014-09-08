class NotAllowedError(Exception):
    def __init__(self):
        self.code = 403


class NotFoundError(Exception):
    def __init__(self):
        self.code = 404


