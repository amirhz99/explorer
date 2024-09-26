from typing import Any

class FastAPIStoreException(Exception):
    pass

class ExploreAlreadyExists(FastAPIStoreException):
    pass

class ExploreNotExists(FastAPIStoreException):
    pass

class InvalidUsernameException(FastAPIStoreException):
    def __init__(self, reason: Any) -> None:
        self.reason = reason