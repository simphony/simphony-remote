from tornado.web import HTTPError


class PayloadedHTTPError(HTTPError):
    def __init__(self, status_code,
                 payload=None,
                 content_type=None,
                 log_message=None,
                 *args, **kwargs):
        """Provides a HTTPError that contains a string payload to output
        as a response. If the payload is None, behaves like a regular
        HTTPError, producing no payload in the response.

        Parameters
        ----------
        payload: str or None
            The payload as a string
        content_type: str or None
            The content type of the payload
        log_message: str or None
            The log message. Passed to the HTTPError.
        """
        super().__init__(status_code, log_message, *args, **kwargs)

        if payload is not None:
            if not isinstance(payload, str):
                raise ValueError("payload must be a string.")

            if content_type is None:
                content_type = "text/plain"
        else:
            if content_type is not None:
                raise ValueError("Content type specified, but no payload")

        self.content_type = content_type
        self.payload = payload
