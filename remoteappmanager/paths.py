"""
Contains the default, absolute disk path of various content.
"""
from os.path import dirname, abspath, join

base_dir = dirname(abspath(__file__))
template_dir = join(base_dir, "templates")
static_dir = join(base_dir, "static")
