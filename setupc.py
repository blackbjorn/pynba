from setuptools import setup, find_packages
from setuptools.extension import Extension
from Cython.Distutils import build_ext

import sys, os

install_requires = [
    'protobuf',
    'werkzeug',
]

setup(name='iscool_e.pynba',
    cmdclass = {'build_ext': build_ext},
    ext_package='iscool_e',
    ext_modules = [Extension("pynba", ["__init__.pyx"])],
    packages=find_packages('src'),
    package_dir = {'': 'src'},
)
