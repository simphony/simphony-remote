import unittest
import os
from jinja2 import Environment, FileSystemLoader

from tests import fixtures
from remoteappmanager.jinja2_adapters import (
    Jinja2LoaderAdapter,
    Jinja2TemplateAdapter)


class TestJinja2Adapters(unittest.TestCase):
    def setUp(self):
        self.template_path = fixtures.get("templates")
        self.jinja_env = Environment(
            loader=FileSystemLoader(
                self.template_path
            ),
            autoescape=True
        )

    def test_initialization(self):
        loader = Jinja2LoaderAdapter(self.jinja_env)
        t = loader.load("foo.html")

        self.assertIsInstance(t, Jinja2TemplateAdapter)

    def test_resolve_path(self):
        loader = Jinja2LoaderAdapter(self.jinja_env)
        path = loader.resolve_path("foo.html")
        self.assertEqual(path, os.path.join(self.template_path, "foo.html"))
        self.assertTrue(os.path.exists(path))

    def test_template_generate(self):
        loader = Jinja2LoaderAdapter(self.jinja_env)
        template = loader.load("foo.html")
        self.assertEqual(template.generate(hello="whatever"), "whatever")

    def test_cache_reset(self):
        loader = Jinja2LoaderAdapter(self.jinja_env)
        self.assertEqual(len(self.jinja_env.cache), 0)
        template = loader.load("foo.html")
        self.assertEqual(template.generate(hello="whatever"), "whatever")
        self.assertEqual(len(self.jinja_env.cache), 1)

        loader.reset()

        self.assertEqual(len(self.jinja_env.cache), 0)
