#!/usr/bin/python
## 
## (C) 2007, 2008, 2013 Muthiah Annamalai,
## Licensed under GPL Version 3
## 
## Interpreter for EXRS language

import os, sys, string, inspect
from Interpreter import Interpreter, REPL, Lex, get_prog_name
from ezhil_parser import EzhilParser
from ezhil_scanner import EzhilLex

if __name__ == "__main__":
    lang = 'ezhil';
    [fname, debug]= get_prog_name(lang)
    if ( fname == "-stdin" or fname == None):
        ## interactive interpreter
        lexer = EzhilLex( )
        parse_eval = Interpreter( lexer, debug )
        parse_eval.change_parser(EzhilParser.factory)
        REPL( lang, lexer, parse_eval, debug )
    else:
        ## evaluate a file
        lexer = EzhilLex(fname)
        if ( debug ): lexer.dump_tokens()
        parse_eval = Interpreter( lexer, debug )
        parse_eval.change_parser(EzhilParser.factory)
        parse_eval.parse()
        if ( debug ):  print "*"*60;  print str(parse_eval)
        env = parse_eval.evaluate()
    pass
