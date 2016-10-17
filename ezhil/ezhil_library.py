## -*- coding: utf-8 -*-
## (C) 2007, 2008, 2013, 2014, 2015 Muthiah Annamalai,
## Licensed under GPL Version 3
##
from __future__ import print_function
import sys
from .runtime import BuiltinFunction

PYTHON3 = (sys.version[0] == '3')

if PYTHON3:
    # For Python 3.0 and later
    from urllib.request import urlopen
else:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

def ezhil_urlopen(*args):
    html = urlopen(*args)
    return html

def ezhil_urlread(html):
    data = html.read()
    if not PYTHON3:
        return data.decode("utf-8")
    return data

def ezhil_urlclose(html):
    html.close()

def Load_URL_APIs(interpreter):
    interpreter.add_builtin("urlopen",ezhil_urlopen,nargin=1,ta_alias="இணைய_இணைப்பு_திற")
    interpreter.add_builtin("urlread",ezhil_urlread,nargin=1,ta_alias="இணைய_இணைப்பு_படி")
    interpreter.add_builtin("urlclose",ezhil_urlclose,nargin=1,ta_alias="இணைய_இணைப்பு_மூடு")
    