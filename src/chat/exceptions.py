from typing import Any

class FastAPIChannelException(Exception):
    pass

class InvalidUsernameException(FastAPIChannelException):
    def __init__(self, reason: Any) -> None:
        self.reason = reason

class ChannelAlreadyExists(FastAPIChannelException):
    pass


class ChannelNotFound(FastAPIChannelException):
    pass