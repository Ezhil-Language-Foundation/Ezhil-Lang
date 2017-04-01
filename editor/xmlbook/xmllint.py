#!/usr/bin/python
# (C) 2017 Ezhil Language Foundation
# 
from __future__ import print_function
from xml.dom.minidom import parse
import sys
for f in sys.argv[1:]:
    data = ('parsing ... %s'%f)
    try:  
        parse(f)
    except Exception as ie:
        print(str(ie))
        print(data+' ... FAIL')
        continue
    print(data+' ... OK')

