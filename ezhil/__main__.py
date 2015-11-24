#!/usr/bin/python
## -*- coding: utf-8 -*-
## (C) 2015 Muthiah Annamalai,
## Licensed under GPL Version 3
## Ezhil PyPi Package

from .ezhil import ezhil_interactive_interpreter as start

# support 'python -m ezhil' syntax
if __name__ == u'__main__':
    start()
