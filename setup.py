from setuptools import setup, Extension
from Cython.Distutils import build_ext
import numpy as np

ext_post_trans = Extension("aro_tools.transpose",
                     ["aro_tools/transpose.pyx", "src/ctranspose.c"],
                     libraries = ["gomp"],
                     include_dirs=[np.get_include(), '/opt/anaconda/include' ],
                     # '-Wa,-q' is max specific and only there because
                     # soemthing is wrong with my gcc. It switches to the
                     # clang assembler.
                     ##extra_compile_args=['-fopenmp', '-O3', '-march=native',
                     ##'-Wa,-q', '-std=c99'],
                     extra_compile_args=['-fopenmp', '-march=native', '-std=c99'],
                     library_dirs = ['/opt/anaconda/lib'],
                     )

EXTENSIONS = [ext_post_trans]



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
    ext_modules = EXTENSIONS,
    cmdclass = {'build_ext': build_ext},

    # metadata for upload to PyPI
    author = "Kiyoshi Wesley Masui, Jonathan Sievers",
    author_email = "kiyo@physics.ubc.ca",
    description = "Tools for ARO FRB search",
    license = "GPL v2.0",
)

