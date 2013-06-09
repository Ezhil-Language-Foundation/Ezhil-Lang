#!/usr/bin/python
## 
## (C) 2007, 2008, 2013 Muthiah Annamalai,
## Licensed under GPL Version 3
## 
## Interpreter for EXRS language

import os, sys, string, inspect
from Interpreter import Interpreter, REPL, Lex
from ezhil_parser import EzhilParser
from ezhil_scanner import EzhilLex

def get_prog_name():
    prog_name=None
    debug=False
    if ( len(sys.argv) < 2 ):
        print "usage: ezhil.py {-stdin|filename} {-debug}"
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
        lang = 'ezhil';
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
    
    ## change a and evaluate Ezhil-language 
    ## evaluate a file

# from ezhil_scanner import *
# from ezhil_parser import *
# from glob import glob
# #["hello.n","fact.n","gcd.n"]:
# for prog in glob("../ezhil_tests/*.n"):
#         f = EzhilLex(prog)
#         f.dump_tokens()
#         fmap = dict(); bmap = dict();
#         p = EzhilParser(f,fmap, bmap,True)
#         ast = p.parse()
#         raise Exception("Not implemented")
#         env = Environment( call_stack, function_map, \
#                            builtin_map, self.debug )
#         env.call_function("__toplevel__") ##some context
#         rval = ast.evaluate(env)
#         print rval
