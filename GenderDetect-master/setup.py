#!/usr/bin/env python
from setuptools import setup, find_packages
import os

from gdetect import config

setup(
      name='GenderDetect',
      version = config.__VERSION__,
      url='https://github.com/Adirockzz95/GenderDetect',
      license='GNU GPL v3',
      author='Aditya Khandkar',
      author_email='khandkar.adi@gmail.com',
      description=('A python wrapper around LIUMs gender detection toolkit.'),
      packages=find_packages(),
      zip_safe=False,
      include_package_data=True,
      package_data = {
            'gdetect': ['*.*']
            },
      classifiers=['Environment :: Console',
                   'Intended Audience :: End Users',
                   'Intended Audience :: Developers',
                   'Programming Language :: Python :: 2.7'
                   'Topic :: Software Development :: Libraries :: Python Modules']
      )
