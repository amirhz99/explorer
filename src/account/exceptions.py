from typing import Any


class FastAPIAccountException(Exception):
    pass


class AccountAlreadyExists(FastAPIAccountException):
    pass


class AccountNotExists(FastAPIAccountException):
    pass


class InvalidUsernameException(FastAPIAccountException):
    def __init__(self, reason: Any) -> None:
        self.reason = reason

