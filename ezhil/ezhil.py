#!/usr/bin/python
# -*- coding: utf-8 -*-
## 
## (C) 2007, 2008, 2013 Muthiah Annamalai,
## Licensed under GPL Version 3
## 
## Interpreter for EXRS language

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

        # input statements
        self.builtin_map["உள்ளீடு"]=self.builtin_map["input"];
        self.builtin_map["சரம்_உள்ளீடு"]=self.builtin_map["raw_input"];
        return
    
if __name__ == "__main__":
    lang = 'ezhil';
    [fname, debug]= get_prog_name(lang)
    if ( fname == "-stdin" or fname == None):
        ## interactive interpreter
        lexer = EzhilLex( )
        parse_eval = EzhilInterpreter( lexer, debug )
        REPL( lang, lexer, parse_eval, debug )
    else:
        ## evaluate a file
        lexer = EzhilLex(fname)
        if ( debug ): lexer.dump_tokens()
        parse_eval = EzhilInterpreter( lexer, debug )
        parse_eval.parse()
        if ( debug ):  print "*"*60;  print str(parse_eval)
        env = parse_eval.evaluate()
    pass
