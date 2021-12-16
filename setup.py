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

requirements = [
    "setuptools>=21.0",
    "traitlets>=4.1",
    "tornado>=4.3",
    "requests>=2.10.0",
    "escapism>=0.0.1",
    "jinja2>=2.8",
    "jupyter_client>=4.3.0",
    "click>=6.6",
    "tabulate>=0.7.5",
    "oauthenticator>=0.5",
]

# Unfortunately RTD cannot install jupyterhub because jupyterhub needs bower,
# and that is not available. We prevent the request for the unreleased jhub
# by skipping it if we are on RTD
# We also have problems with requests as docker-py wants <2.11 and RTD
# provides 2.11.1

on_rtd = os.environ.get('READTHEDOCS') == 'True'
if on_rtd:
    # These are the dependencies of jupyterhub that we need to have in order
    # for our code to import on RTD.
    requirements.extend(["sqlalchemy>=1.0"])
else:
    requirements.extend([
        "jupyterhub>0.7",
        "docker-py==1.8",
        "tornadowebapi>=0.5.0"])


class install(_install):
    def run(self):
        if not on_rtd:
            import subprocess
            subprocess.check_call(['npm', 'run', 'build'])
        # Workaround for setuptools ignoring `install_requires` when
        # `cmdclass` is overridden. See https://stackoverflow.com/q/21915469
        super().do_egg_install()


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
