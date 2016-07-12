class BaseException(Exception):
    """Base exception for the REST infrastructure"""
    pass


class NotFound(BaseException):
    """Exception raised when the resource is not found.
    Raise this exception in your CRUD handlers when you can't
    find the resource the identifier refers to.
    """
    pass


class UnprocessableRepresentation(BaseException):
    """Exception raised when the resource representation is
    invalid or does not contain the appropriate keys.
    Raise this exception in your CRUD handlers when the received
    representation is ill-formed"""
    pass
