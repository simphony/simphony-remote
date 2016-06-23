import os
base_path = os.path.dirname(os.path.abspath(__file__))


def get(fixture):
    """Retrieve the absolute path of the fixture"""
    return os.path.join(base_path, fixture)
