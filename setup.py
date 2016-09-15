from setuptools import setup, find_packages

from remoteappmanager import __version__

VERSION = __version__

import os

requirements=[
    "setuptools>=21.0",
    "traitlets>=4.1",
    "tornado>=4.3",
    "docker-py>=1.8",
    "requests>=2.10.0",
    "escapism>=0.0.1",
    "jinja2>=2.8",
    "jupyter_client>=4.3.0",
    "click>=6.6",
    "tabulate>=0.7.5",
]


# Unfortunately RTD cannot install jupyterhub because jupyterhub needs bower,
# and that is not available. We prevent the request for the unreleased jhub
# by skipping it if we are on RTD
on_rtd = os.environ.get('READTHEDOCS') == 'True'
if not on_rtd:
    requirements.append("jupyterhub>=0.7.0dev0")

# main setup configuration class
setup(
    name='remoteappmanager',
    version=VERSION,
    author='SimPhoNy Project',
    description='Remote application manager sub-executable',
    install_requires=requirements,
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            "remoteappmanager = remoteappmanager.__main__:main",
            "remoteappdb = remoteappmanager.cli.remoteappdb.__main__:main",
            "remoteapprest = remoteappmanager.cli.remoteapprest.__main__:main"
            ]
        }
    )
