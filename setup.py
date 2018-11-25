"""
file: setup.py

Description: Simple script to compile 'reversi.pyx' with Cython. Gives
approximately 2x speed boost over cPython.
"""

from distutils.core import setup
from Cython.Build import cythonize
from distutils.extension import Extension
from Cython.Distutils import build_ext

setup(
    name = "reversi",
    cmdclass = {"build_ext": build_ext},
    ext_modules =
    [
        Extension("reversi",
                  ["reversi.pyx"],
                  extra_compile_args = ["-O3", "-fopenmp"],
                  extra_link_args=['-fopenmp']
        )
    ]
)

