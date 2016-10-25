import functools

from tornadowebapi.exceptions import NotFound


def authenticated(method):
    """Validates if the user is recognized before allowing
    access to a resource."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.current_user is None:
            raise NotFound()

        return method(self, *args, **kwargs)

    return wrapper
