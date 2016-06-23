from setuptools import setup, find_packages

from remoteappmanager import __version__

VERSION = __version__

with open("requirements.txt") as f:
    INSTALL_REQUIRES = f.readlines()

# main setup configuration class
setup(
    name='remoteappmanager',
    version=VERSION,
    author='SimPhoNy Project',
    description='Remote application manager sub-executable',
    install_requires=INSTALL_REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            "remoteappmanager = remoteappmanager.__main__:main"
            ]
        }
    )
