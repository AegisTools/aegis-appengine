class NotAllowedError(Exception):
    def __init__(self):
        self.code = 403


class NotFoundError(Exception):
    def __init__(self):
        self.code = 404


class IllegalError(Exception):
    def __init__(self, message):
        super(IllegalError, self).__init__(message)
        self.code = 400
