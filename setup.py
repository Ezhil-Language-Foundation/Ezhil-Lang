#!/usr/bin/env python

from distutils.core import setup
from codecs import open

setup(name='ezhil',
      version='0.1-dev',
      description='Python library for Tamil programming language Ezhil',
      author='Muthiah Annamalai',
      author_email='muthuspost@gmail.com',
      url='https://github.com/arcturusannamalai/Ezhil-Lang',
      packages=['ezhil'],
      license='GPLv3',
      platforms='PC,Linux,Mac',
      classifiers='Natural Language :: Tamil',
      long_description=open('README.md','r','UTF-8').read(),
      download_url='https://github.com/arcturusannamalai/Ezhil-Lang/archive/latest.zip',#pip
      )
