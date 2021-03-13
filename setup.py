#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# (C) 2008-2017,2021 முத்தையா அண்ணாமலை 
# ezhil language project


# specify dependecies properly
from setuptools import setup
# from distutils.core import setup
from codecs import open

setup(name='ezhil',
      version='1.0',
      description='Ezhil - Tamil programming language implemented in Python; Ezhil works on Python 3',
      author='Muthiah Annamalai',
      author_email='ezhillang@gmail.com',
      url='https://github.com/Ezhil-Language-Foundation/Ezhil-Lang',
      packages=['ezhil'],
      license='GPLv3',
      platforms='PC,Linux,Mac',
      classifiers=['Natural Language :: Tamil',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9'],
      install_requires=["open-tamil", "argparse"],
      entry_points={'console_scripts': [
          'ezhili = ezhil.ezhil:main',
          ]
      },
      long_description='Ezhil is a Tamil programming language for early education',
      download_url='https://github.com/Ezhil-Language-Foundation/Ezhil-Lang/archive/latest.zip',
      )

