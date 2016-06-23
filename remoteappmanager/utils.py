def with_end_slash(url):
    """Normalises a url to have an ending slash, and only one."""
    return url.rstrip("/")+"/"
