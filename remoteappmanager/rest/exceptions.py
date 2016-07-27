from remoteappmanager.rest import httpstatus


class RESTException(Exception):
    """Base exception for the REST infrastructure
    These are exceptions that can be raised by the CRUD handlers.
    """
    #: HTTP code generally associated to this exception.
    #: Missing any better info, default is a server error.
    http_code = httpstatus.INTERNAL_SERVER_ERROR


class NotFound(RESTException):
    """Exception raised when the resource is not found.
    Raise this exception in your CRUD handlers when you can't
    find the resource the identifier refers to.
    """
    http_code = httpstatus.NOT_FOUND


class BadRequest(RESTException):
    """Exception raised when the resource representation is
    invalid or does not contain the appropriate keys.
    Raise this exception in your CRUD handlers when the received
    representation is ill-formed
    """
    http_code = httpstatus.BAD_REQUEST


class InternalServerError(RESTException):
    pass
