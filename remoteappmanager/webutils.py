class Link:
    """Class to represent a link in our jinja tabular template mechanics"""
    def __init__(self, text, rel_urlpath):
        """
        Parameters
        ----------
        text:
            the link text
        rel_urlpath:
            The path of the link, relative to the base_url template parameter.
        """
        self.text = text
        self.rel_urlpath = rel_urlpath


def is_link(obj):
    """Jinja custom test. Returns True if the object obj is a Link"""
    return isinstance(obj, Link)
