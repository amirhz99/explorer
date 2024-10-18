from typing import Any

class FastAPIStoreException(Exception):
    pass

class SearchAlreadyExists(FastAPIStoreException):
    pass

class SearchNotExists(FastAPIStoreException):
    pass

class InvalidUsernameException(FastAPIStoreException):
    def __init__(self, reason: Any) -> None:
        self.reason = reason