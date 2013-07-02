#!/usr/bin/python
# -*- coding: utf-8 -*-
## 
## (C) 2007, 2008, 2013 Muthiah Annamalai,
## Licensed under GPL Version 3
## 
## Interpreter for Ezhil language

import os, sys, string, inspect
from Interpreter import Interpreter, REPL, Lex, get_prog_name
from ezhil_parser import EzhilParser
from ezhil_scanner import EzhilLex

class EzhilInterpreter( Interpreter ):
    def __init__(self, lexer, debug ):
        Interpreter.__init__(self,lexer,debug)
        Interpreter.change_parser(self,EzhilParser.factory)
        return
    
    def install_builtins(self):
        """ populate with the builtin functions, while adding our own flavors"""
        Interpreter.install_builtins(self)
        
        #input statements, length constructs
        tamil_equiv = {"சரம்_இடமாற்று":"replace",            "சரம்_கண்டுபிடி":"find",         "நீளம்":"len",
                                "சரம்_உள்ளீடு":"raw_input",       "உள்ளீடு" : "input" }
        #list operators        
        tamil_equiv.update( {"பட்டியல்":"list","பின்இணை":"append","தலைகீழ்":"reverse",
                                         "வரிசைப்படுத்து":"sort","நீட்டிக்க":"extend","நுழைக்க":"insert","குறியீட்டெண்":"index",
                                         "வெளியேஎடு":"pop","பொருந்தியஎண்":"count", "எடு":"get"} )
        
        #file operators
        tamil_equiv.update({"கோப்பை_திற":"file_open", "கோப்பை_மூடு":"file_close","கோப்பை_படி":"file_read",
                            "கோப்பை_எழுது":"file_write","கோப்பை_எழுது_வரிகள்":"file_writelines","கோப்பை_படி_வரிகள்":"file_readlines"})
        
        for k,v in list(tamil_equiv.items()):
            self.builtin_map[k]=self.builtin_map[v];
        
        # translations for turtle module
        turtle_map = { "முன்னாடி":"forward", "பின்னாடி" :"backward",
                       "வலது":"lt", "இடது":"rt",
                       "எழுதுகோல்மேலே":"penup",  "எழுதுகோல்கிழே":"pendown"}
        for k,v in list(turtle_map.items()):
            vv = "turtle_"+v;
            self.builtin_map[k] = self.builtin_map[vv]
        
        return
    
if __name__ == "__main__":
    lang = 'ezhil';
    [fname, debug, dostdin ]= get_prog_name(lang)
    if ( dostdin ):
        ## interactive interpreter
        lexer = EzhilLex( )
        parse_eval = EzhilInterpreter( lexer, debug )
        REPL( lang, lexer, parse_eval, debug )
    else:
        ## evaluate a files sequentially
        for files in fname:
            lexer = EzhilLex(files)
            if ( debug ): lexer.dump_tokens()
            parse_eval = EzhilInterpreter( lexer, debug )
            parse_eval.parse()
            if ( debug ):  print("*"*60);  print(str(parse_eval))
            env = parse_eval.evaluate()
        
    pass
