#!/usr/bin/python
# (C) 2017 Ezhil Language Foundation
# 

from xml.dom.minidom import parse
import sys
import glob

def do_check(args):
    for f in args:
        data = ('parsing ... %s'%f)
        try:
            parse(f)
        except Exception as ie:
            print(str(ie))
            print(data+' ... FAIL')
            continue
        print(data+' ... OK')

if __name__ == "__main__":
    if len(sys.argv) > 1:
        do_check(sys.argv[1:])
    else:
        do_check(glob.glob("*.xml"))
