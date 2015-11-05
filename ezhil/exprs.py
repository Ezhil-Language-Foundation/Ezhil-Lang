#!/usr/bin/python
##
## (C) 2007, 2008, 2013 Muthiah Annamalai,
## Licensed under GPL Version 3
##
## Interpreter for EXRS language 

import os, sys, string, inspect, codecs
from Interpreter import Interpreter, REPL, Lex, get_prog_name

sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
#sys.stdin = codecs.getreader('utf-8')(sys.stdin)

if __name__ == "__main__":      
    lang = 'exprs';
    [fname, debug, dostdin, encoding ]= get_prog_name(lang)
    # don't care about encoding right now
    if ( dostdin ):
        ## interactive interpreter
        lexer = Lex( )
        parse_eval = Interpreter( lexer, debug )
        REPL( lang, lexer, parse_eval, debug )
    else:
        ## evaluate a files sequentially
        for files in fname:
            ## evaluate a file
            lexer = Lex(files)
            if ( debug ): lexer.dump_tokens()
            parse_eval = Interpreter( lexer, debug )  
            parse_eval.parse()
            if ( debug ):  print("*"*60);  print(str(parse_eval))
            env = parse_eval.evaluate()
    pass
