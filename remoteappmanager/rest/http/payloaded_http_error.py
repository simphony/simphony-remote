from tornado.web import HTTPError


class PayloadedHTTPError(HTTPError):
    def __init__(self, status_code, payload=None, log_message=None,
                 *args, **kwargs):
        """Provides a HTTPError that contains a string payload to output
        as a response. If the payload is None, behaves like a regular
        HTTPError, producing no payload in the response.
        """
        super().__init__(status_code, log_message, *args, **kwargs)

        if payload is not None and not isinstance(payload, str):
            raise ValueError("payload must be a string.")

        self.payload = payload
