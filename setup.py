from setuptools import setup

VERSION_MAJOR = 0
VERSION_MINOR = 1
VERSION_POINT = 0
VERSION_DEV = 1

VERSION = "%d.%d.%d" % (VERSION_MAJOR, VERSION_MINOR, VERSION_POINT)
if VERSION_DEV:
    VERSION = VERSION + ".dev%d" % VERSION_DEV




setup(
    name = 'aro_tools',
    version = VERSION,
    packages = ['aro_tools'],

    # metadata for upload to PyPI
    author = "Kiyoshi Wesley Masui, Jonathan Sievers",
    author_email = "kiyo@physics.ubc.ca",
    description = "Tools for ARO FRB search",
    license = "GPL v2.0",
)

