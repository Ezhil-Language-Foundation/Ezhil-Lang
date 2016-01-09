#!/usr/bin/python
## -*- coding: utf-8 -*-
## (C) 2015 Muthiah Annamalai,
## Licensed under GPL Version 3
## Ezhil PyPi Package

from .ezhil import main

# support 'python -m ezhil' syntax 
# including running files specified at CLI
if __name__ == u'__main__':
    main()
