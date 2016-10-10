class UnsupportedOperation(Exception):
    """Raised when the operation is unsupported by the backend."""


class Exists(Exception):
    """
    Raised when a create operation fails because the entity
    is already present
    """


class NotFound(Exception):
    """
    Raised when a remove operation fails because the entity
    is not found
    """
