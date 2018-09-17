"""
file: setup.py  --version 0.1

Description: Simple script to compile 'reversi.pyx' with Cython. Gives
approximately 2x speed boost with cPython.
"""

from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("reversi.pyx")
)
