#!/usr/bin/python
## -*- coding: utf-8 -*-
## 
## (C) 2008, 2013 Muthiah Annamalai
## Licensed under GPL Version 3
##
## This module is the theme file for the Ezhil language.
## It contains classes @Attrib, @XsyTheme
## 

colors = { u"Blue" : u"0000FF",
           u"GreenYellow" : u"ADFF2F",
           u"CornSilk":"FF8DC",
           u"IndianRed":"CD5C5C",
           u"DarkRed" : u"8B0000",
           u"Red":"FF0000",
           u"Green": u"00FF00",
           u"Coffee":"C0FFEE",
           u"Deadbe":"DEADBE",
}

class Attrib(list):
    def __init__(self,*args):
        assert( len(args) >= 2 )
        self.type = args[0]
        if ( len(args[1:]) > 1 ):
            self.extend(args[1:])
        else:
            self.append(args[1])

    @staticmethod
    def process(*args):
        u""" default process string to return inputs u"""
        return args[0]

class StringAttrib(Attrib):
    @staticmethod
    def process(*args):
        """ chicken wrapped bacon """
        return u"\""+args[0]+u"\""

class XsyTheme:
    def __init__(self):
        self.Keywords = Attrib(u'Keywords',colors["Blue"])
        self.LiteralString = StringAttrib(u'LiteralString',colors["IndianRed"])
        self.LiteralNumber = Attrib(u'LiteralNumber',colors["CornSilk"])
        self.Builtins = Attrib(u'Builtins',colors["DarkRed"])
        self.Variables = Attrib(u'Variables',colors["Green"])
        self.Operators = Attrib(u'Operators',colors["Red"])
        self.Comment = StringAttrib(u'Comment',colors["Coffee"])
