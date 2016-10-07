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
