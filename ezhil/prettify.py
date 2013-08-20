#!/usr/bin/python
## -*- coding: utf-8 -*-
## 
## (C) 2008, 2013 Muthiah Annamalai
## Licensed under GPL Version 3
##
## This module is the pretty-printer for the Ezhil language.
## It contains classes @WikiStyle, @Printer
## 

from theme import XsyTheme
from ezhil_scanner import EzhilLex, EzhilToken
from ezhil import EzhilInterpreter
from transformer import Visitor

class WikiStyle:
    @staticmethod
    def wrap_msg(attrib,text):
        """ @text is any character stream that has to be wrapper in a style-Theme,
            specified by @attrib """
        if ( len(attrib) >= 1 ):
            out = '<span style="color:#'+attrib[0]
        if ( len(attrib) >= 2 ):
            out = out + ';background:#'+attrib[1]
        out = out + '">' + text + "</span>"
        return out

class Printer:
    def __init__(self,src_file):
        self.styler = WikiStyle.wrap_msg
        self.theme = XsyTheme()
        self.lexer = EzhilLex(src_file)
        self.lexer.tokens.reverse()
    
    def pretty_printer(self):
        # raise Exception("Kaput .. not implemented")
        
    
    # method walks the lexer-tokens and calls the appropriate elements
    def hilite(self):
        out = []
        for t in self.lexer.tokens:
            add_br = False
            attrib = self.theme.Operators
            if EzhilToken.is_keyword(t.kind):
                attrib = self.theme.Keywords
                if ( EzhilToken.get_name(t.kind) in ["END", "ELSE"] ):
                    out.append('<BR />\n')
            elif EzhilToken.is_number(t.kind):
                attrib = self.theme.LiteralNumber                
            elif EzhilToken.is_string(t.kind):
                attrib = self.theme.LiteralString
                t.val = '"'+t.val+'"' #FIXME: ideally do some escaping as well
            elif EzhilToken.is_id(t.kind):                
                attrib = self.theme.Variables
            elif( t.val in ["@", "பதிப்பி" ] ):
                attrib = self.theme.Builtins
                out.append('<BR />\n')                

            t.val = " " + str(t.val)
            out.append( self.styler(attrib,t.val) )
            if ( add_br ):
                out.append("<BR />\n")
        
        return "".join(out)
    
if __name__ == "__main__":
    from sys import argv
    for aFile in argv[1:]:
        print "working with ",aFile
        print Printer(aFile).hilite()
    
