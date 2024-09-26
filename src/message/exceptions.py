from typing import Any


class FastAPIMessageException(Exception):
    pass


class MessageAlreadyExists(FastAPIMessageException):
    pass


class MessageNotExists(FastAPIMessageException):
    pass


class InvalidUsernameException(FastAPIMessageException):
    def __init__(self, reason: Any) -> None:
        self.reason = reason

