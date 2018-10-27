"""
file: setup.py

Description: Simple script to compile 'reversi.pyx' with Cython. Gives
approximately 1x speed boost over cPython.
"""

from Cython.Build import cythonize
from distutils.core import setup

setup(
    ext_modules=cythonize("reversi.pyx")
)
