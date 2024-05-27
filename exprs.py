#!/usr/bin/python
# -*- coding: utf-8 -*-
## 
## (C) 2007-2016 Muthiah Annamalai,
## Licensed under GPL Version 3
import sys
import codecs
from ezhil import exprs_eval

PYTHON3 = (sys.version[0] == '3')
if PYTHON3:
    str = str
else:
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    #sys.stdin = codecs.getreader('utf-8')(sys.stdin)

if __name__ == "__main__":
    exprs_eval()
