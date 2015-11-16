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
    [fname, debug, dostdin, encoding,stacksize,profile]= get_prog_name(lang)
    update=True;  safe_mode=True;
    # don't care about encoding right now
    if ( dostdin ):
        ## interactive interpreter
        lexer = Lex( )
        parse_eval = Interpreter( lexer, debug, safe_mode,update,stacksize )
        REPL( lang, lexer, parse_eval, debug )
    else:
        ## evaluate a files sequentially
        exitcode = 0
        for files in fname:
            ## evaluate a file
            lexer = Lex(files)
            if ( debug ): lexer.dump_tokens()
            parse_eval = Interpreter( lexer, debug, safe_mode, update, stacksize )  

            try:
                parse_eval.parse()
            except Exception as e:
                print(u"parsing the code '%s' failed with exception:\n\t %s"%(files,str(e)))
                if ( debug ):  print("*"*60);  print(str(parse_eval))
                exitcode = 255
                
            try:
                env = parse_eval.evaluate()
            except Exception as e:
                print(u"evaluating the code '%s' failed with exception:\n\t %s"%(files,str(e)))
                if debug: print("*"*60);  print(str(e))
                exitcode = 255
        sys.exit(exitcode)
    pass
