import hashlib

from tornado.template import Template


class Jinja2LoaderAdapter:
    """Adapts the Jinja2 environment to act as a loader
    as desired by tornado.

    The class uses duck typing to implement the interface of tornado.BaseLoader
    and relies on jinja caching to hold the premade templates.
    """
    def __init__(self, env):
        """Initializes the adapter.

        Parameters
        ----------
        env : Environment
            the jinja2 environment

        """
        self._env = env

    def reset(self):
        """Resets the LRU cache in jinja template environment.
        The method is already thread safe.
        """
        self._env.cache.clear()

    def load(self, name, parent_path=None):
        """Loads the template with a given name.

        Parameters
        ----------
        name : str
            the simple name of the template.
        parent_path : str
            The parent path (unused)

        Return
        ------
        Jinja2TemplateAdapter object, adapting a jinja template into a tornado
        template interface
        """
        return Jinja2TemplateAdapter(self._env.get_template(name))

    def resolve_path(self, name, parent_path=None):
        """Returns the absolute name of the template according to the loader.

        Parameters
        ----------
        name : str
            the simple name of the template.
        parent_path : str
            The parent path (unused)

        Return
        ------
        The absolute path of the template
        """
        _, filename, _ = self._env.loader.get_source(self._env, name)
        return filename


class Jinja2TemplateAdapter(Template):
    """Adapts the Jinja template interface to act as a tornado template.
    It reimplements the base class, but it uses no functionality of it.

    """
    def __init__(self, template):
        self._template = template

    def generate(self, **kwargs):
        """Generate this template with the given arguments."""
        return self._template.render(**kwargs)


def gravatar_id(value):
    """Computes the gravatar identifier for a given value (normally email)
    Used for jinja filter."""
    return hashlib.md5(str(value).strip().lower().encode("utf-8")).hexdigest()
