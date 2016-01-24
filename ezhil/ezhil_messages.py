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

# set default language as English for testing
class Messages:
    SOURCE_LANGUAGE = u"EN"
    LANGUAGE_INDEX = {u"EN":0,u"TA":1}

    UnexpectedNumber = 1
    ClassNotFound = 2
    CaseSyntaxError = 3
    IfSyntaxError = 4
    GenSyntaxError = 5
    catalog = {
            UnexpectedNumber : ("Expected Number, found something %s",u"எதிர்பாராத எழுத்துக்கள் உள்ளீடில் வந்தன, %s; எண்கள் மட்டுமே வரலாம்"),
            ClassNotFound:(u"Cannot find %s class",u"%s என்ற நிரல் தொகுப்பை காணவில்லை"),
            CaseSyntaxError : (u"SWITCH-CASE-OTHERWISE : Syntax error in this statement",u"செய் தேர்ந்தெடு வாக்கியம் பிழையாக உள்ளது"),
            IfSyntaxError : (u"If-Else-If statement syntax is messed up",u"ஆனால் இல்லையானால் வாக்கியம்  பிழையாக உள்ளது"),
            GenSyntaxError : (u"Syntax error in program",u"வாக்கியம்  பிழையாக உள்ளத")
        }
    @staticmethod
    def set_language(srclang):
        Messages.SOURCE_LANGUAGE=srclang

    @staticmethod
    def format(id,args=None):
        lang_idx = Messages.LANGUAGE_INDEX[Messages.SOURCE_LANGUAGE]
        fmt = Messages.catalog[id]
        if args:
            msg = fmt[lang_idx]%(args)
        else:
            msg = fmt[lang_idx]
        return msg

def set_language(lang):
    Messages.set_language(lang)
    return

def get_message(id,args):
    return Messages.format(id,args)
