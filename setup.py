#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# (C) 2008-2016 முத்தையா அண்ணாமலை 
# ezhil language project

try:
    # specify dependecies properly
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from codecs import open

setup(name='ezhil',
      version='0.82',
      description='Ezhil - Tamil programming language implemented in Python',
      author='Muthiah Annamalai',
      author_email='ezhillang@gmail.com',
      url='https://github.com/arcturusannamalai/Ezhil-Lang',
      packages=['ezhil'],
      license='GPLv3',
      platforms='PC,Linux,Mac',
      classifiers='Natural Language :: Tamil',
      install_requires=["open-tamil", "argparse"],
      entry_points={'console_scripts': [
          'ezhili = ezhil.ezhil:main',
          ]
      },
      long_description='Ezhil is a Tamil programming language for early education',
      download_url='https://github.com/arcturusannamalai/Ezhil-Lang/archive/latest.zip',
      )
