## -*- coding: utf-8 -*-
## (C) 2016 Muthiah Annamalai,
## Licensed under GPL Version 3
##
## This class allows you to get translated messages
## It is sort of like gettext

from __future__ import print_function
import sys

WINDOWS = sys.platform.find("win") >= 0
PYTHON3 = (sys.version[0] == '3')

if PYTHON3:
    unicode = str

class Messages:
    UnexpectedNumber = 1
    ClassNotFound = 2
    catalog = {
            UnexpectedNumber : ("Expected Number, found something %s",u"எதிர்பாராத எழுத்துக்கள் உள்ளீடில் வந்தன, %s; எண்கள் மட்டுமே வரலாம்"),
            ClassNotFound:(u"Cannot find %s class",u"%s என்ற நிரல் தொகுப்பை காணவில்லை")
        }

    @staticmethod
    def format(id,args=None):
        lang_idx = (not WINDOWS) and 1 or 0
        fmt = Messages.catalog[id]
        if args:
            msg = fmt[lang_idx]%(args)
        else:
            msg = fmt[lang_idx]
        return msg

def get_message(id,args):
    return Messages.format(id,args)
