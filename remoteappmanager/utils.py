import inspect
from functools import wraps
import warnings


def url_path_join(*pieces):
    """Join components of url into a relative url path
    Use to prevent double slash when joining subpath. This will leave the
    initial and final / in place

    Assume pieces do not contain protocol (e.g. http://)
    """
    stripped = [s.strip('/') for s in pieces]
    result = '/'.join(s for s in stripped if s)

    if pieces[0].startswith('/'):
        result = '/' + result

    if pieces[-1].endswith('/'):
        result = result + '/'

    if result == '//':
        result = '/'

    return result


def with_end_slash(url):
    """Normalises a url to have an ending slash, and only one."""
    return url.rstrip("/")+"/"


def without_end_slash(url):
    """Makes sure there is no end slash at the end of a url."""
    return url.rstrip("/")


def parse_volume_string(volume_string):
    """Parses a volume specification string SOURCE:TARGET:MODE into
    its components, or raises click.BadOptionUsage if not according
    to format."""
    try:
        source, target, mode = volume_string.split(":")
    except ValueError:
        raise ValueError("Volume string must be in the form "
                         "source:target:mode")

    if mode not in ('rw', 'ro'):
        raise ValueError("Volume mode must be either 'ro' or 'rw'")

    return source, target, mode


def mergedoc(function, other):
    """ Merge the docstring from the other function to the decorated function.

    """
    if other.__doc__ is None:
        return function
    elif function.__doc__ is None:
        function.__doc__ = other.__doc__
        return function
    else:
        merged_doc = '\n'.join((other.__doc__, function.__doc__))
        function.__doc__ = merged_doc
        return function


class mergedocs(object):
    """ Merge the docstrings of other class to the decorated.

    """
    def __init__(self, other):
        self.other = other

    def __call__(self, cls):
        for name, old in inspect.getmembers(self.other):
            if inspect.isfunction(old):
                new = getattr(cls, name, None)
                if new is not None:
                    mergedoc(new, old)
        return cls


def one(elements):
    """Returns True if only one element is not None, false otherwise"""
    return sum([False if e is None else True for e in elements]) == 1


def remove_quotes(s):
    """Removes start/end quotes from a string, if needed.
    If s is not a string, it is returned untouched.
    """
    if not isinstance(s, str):
        return s

    if len(s) < 2:
        return s

    if s[0]+s[-1] in ['""', "''"]:
        return s[1:-1]

    return s


def deprecated(func):
    """Decorator. Marks a function/method as deprecated."""
    @wraps(func)
    def _deprecated(*args, **kwargs):
        warnings.warn("Deprecation warning: {}".format(func.__name__))
        return func(*args, **kwargs)

    return _deprecated
