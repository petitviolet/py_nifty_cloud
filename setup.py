# -*- encoding:utf-8 -*-
from setuptools import setup, find_packages
from py_nifty_cloud import (__author__, __license__, __version__)

setup(
    version=__version__,
    author=__author__,
    license=__license__,
    name='py_nifty_cloud',
    author_email='violethero0820@gmail.com',
    packages=find_packages(),
    description = 'wrapper for request to Nifty Cloud mobile backend',
    long_description = 'Please show help (py_nifty_cloud -h)',
    url = 'https://github.com/petitviolet/py_nifty_cloud',
    platforms = ['Mac OS X'],
    zip_safe=False,
    install_requires = ['requests', 'pyyaml'],
    classifiers=[
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Software Development',
    ],
)
