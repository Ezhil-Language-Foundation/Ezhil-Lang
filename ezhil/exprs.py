#!/usr/bin/python
##
## (C) 2007, 2008, 2013 Muthiah Annamalai,
## Licensed under GPL Version 3
##
## Interpreter for EXRS language 

import os, sys, string, inspect
from Interpreter import Interpreter, REPL, Lex

def get_prog_name():
    prog_name=None
    debug=False
    if ( len(sys.argv) < 2 ):
        print "usage: exprs.py {-stdin|filename} {-debug}"
        sys.exit(-1)
    
    if ( len(sys.argv) >= 2 ):
        prog_name=sys.argv[1]
    if ( len(sys.argv) >= 3 ):
        debug = (sys.argv[2] == "-debug")
    return [prog_name, debug]

if __name__ == "__main__":      
    [fname, debug]= get_prog_name()    
    if ( fname == "-stdin" or fname == None):
        ## interactive interpreter
        lang = 'exprs';        
        lexer = Lex( )
        parse_eval = Interpreter( lexer, debug )
        REPL( lang, lexer, parse_eval, debug )
    else:
        ## evaluate a file
        lexer = Lex(fname)       
        if ( debug ): lexer.dump_tokens()
        parse_eval = Interpreter( lexer, debug )  
        parse_eval.parse()
        if ( debug ):  print "*"*60;  print str(parse_eval)
        env = parse_eval.evaluate()
