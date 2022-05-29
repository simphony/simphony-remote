import os
from setuptools import setup, find_packages
from setuptools.command.install import install as _install

# Setup version
VERSION = '2.2.0.dev'

# Read description
with open('README.rst', 'r') as readme:
    README_TEXT = readme.read()


def write_version_py():
    filename = os.path.join(
        os.path.dirname(__file__),
        'remoteappmanager',
        'version.py')
    ver = "__version__ = '{}'\n"
    with open(filename, 'w') as fh:
        fh.write("# Autogenerated by setup.py\n")
        fh.write(ver.format(VERSION))


write_version_py()

# Unfortunately RTD cannot install jupyterhub because jupyterhub needs bower,
# and that is not available. We prevent the request for the unreleased jhub
# by skipping it if we are on RTD

on_rtd = os.environ.get('READTHEDOCS') == 'True'
if on_rtd:
    # These are the dependencies of jupyterhub that we need to have in order
    # for our code to import on RTD.
    requirements = [
        "setuptools>=21.0",
        "traitlets>=4.1",
        "tornado>=4.3",
        "requests>=2.10.0",
        "escapism>=0.0.1",
        "jupyter_client>=4.3.0",
        "click>=6.6",
        "tabulate>=0.7.5",
        "oauthenticator>=0.5",
        "sqlalchemy<1.4",
        # Pinning jinja2 requirements when building on RTD due to
        # regression when using old versions of sphinx<2
        # https://github.com/readthedocs/readthedocs.org/issues/9037
        "jinja2<3.1.0",
    ]
else:
    with open('requirements.txt', 'r') as REQUIREMENTS:
        requirements = [
            line.strip() for line in REQUIREMENTS.readlines()
            if not line.startswith('#')
        ]


class install(_install):
    def run(self):
        if not on_rtd:
            import subprocess
            subprocess.check_call(['npm', 'run', 'build'])
        super().run()


# main setup configuration class
setup(
    name='remoteappmanager',
    version=VERSION,
    author='SimPhoNy Project',
    description='Remote application manager sub-executable',
    long_description=README_TEXT,
    install_requires=requirements,
    packages=find_packages(exclude=["selenium_tests"]),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            "remoteappmanager = " +
                "remoteappmanager.cli.remoteappmanager.__main__:main",
            "remoteappadmin = " +
                "remoteappmanager.cli.remoteappadmin.__main__:main",
            "remoteappdb = remoteappmanager.cli.remoteappdb.__main__:main",
            "remoteapprest = remoteappmanager.cli.remoteapprest.__main__:main"
            ]
        },
    cmdclass={'install': install}
    )
