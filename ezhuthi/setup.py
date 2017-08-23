#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# (C) 2017 Ezhil Language Foundation
#  முத்தையா அண்ணாமலை  <ezhillang@gmail.com>
# This file is part of Ezhil Language Project

try:
    # specify dependecies properly
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from codecs import open

setup(name='ezhuthi',
      version='1',
      description='Ezhuthi - a GTK based GUI for Ezhil (Tamil programming language) Python 2 and Python 3',
      author='Muthiah Annamalai',
      author_email='ezhillang@gmail.com',
      url='https://github.com/Ezhil-Language-Foundation/Ezhil-Lang',
      packages=['ezhuthi'],
      package_dir={'ezhuthi': 'ezhuthi'},
      package_data={'ezhuthi': ['res/*.*','res/img/*','xmlbook/*']},
      license='GPLv3',
      platforms='PC,Linux,Mac',
      classifiers=['Natural Language :: Tamil',
          'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4'],
      install_requires=["ezhil","pygobject","open-tamil", "argparse"],
      entry_points={'console_scripts': [
          'ezhuthi = ezhuthi.ezhuthi:main',
          ]
      },
      long_description='Ezhil is a Tamil programming language for early education',
      download_url='https://github.com/Ezhil-Language-Foundation/Ezhil-Lang/archive/latest.zip',
      )
