#!/usr/bin/python
## -*- coding: utf-8 -*-
## 
## (C) 2008, 2013 Muthiah Annamalai
## Licensed under GPL Version 3
##
## This module is the theme file for the Ezhil language.
## It contains classes @Attrib, @XsyTheme
## 

colors = { "Blue" : "0000FF",
           "GreenYellow" : "ADFF2F",
           "CornSilk":"FF8DC",
           "IndianRed":"CD5C5C",
           "DarkRed" : "8B0000",
           "Green": "00FF00",
           "Coffee":"C0FFEE",
           "Deadbe":"DEADBE",
};

class Attrib(list):
    def __init__(self,*args):
        assert( len(args) >= 2 )
        self.type = args[0]
        if ( len(args[1:]) > 1 ):
            self.extend(args[1:])
        else:
            self.append(args[1])
        

class XsyTheme:
    def __init__(self):
        self.Keywords = Attrib('Keywords',colors["Blue"])
        self.LiteralString = Attrib('LiteralString',colors["IndianRed"])
        self.LiteralNumber = Attrib('LiteralNumber',colors["CornSilk"])
        self.Builtins = Attrib('Builtins',colors["DarkRed"])
        self.Variables = Attrib('Variables',colors["Green"])
        self.Operators = Attrib('Operators',colors["Red"])
