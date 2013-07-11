#!/usr/bin/python
# -*- coding: utf-8 -*-
## 
## (C) 2007, 2008, 2013 Muthiah Annamalai,
## Licensed under GPL Version 3
## 
## Interpreter for Ezhil language

import os, sys, string, tempfile
from Interpreter import Interpreter, REPL, Lex, get_prog_name
from ezhil_parser import EzhilParser
from ezhil_scanner import EzhilLex
from errors import RuntimeException, ParseException

class EzhilInterpreter( Interpreter ):
    def __init__(self, lexer, debug ):
        Interpreter.__init__(self,lexer,debug)
        Interpreter.change_parser(self,EzhilParser.factory)
        return
    
    def install_builtins(self):
        """ populate with the builtin functions, while adding our own flavors"""
        Interpreter.install_builtins(self)
        
        #input statements, length constructs
        tamil_equiv = {"சரம்_இடமாற்று":"replace", "சரம்_கண்டுபிடி":"find","நீளம்":"len",
                       "சரம்_உள்ளீடு":"raw_input", "உள்ளீடு" : "input" }
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

class EzhilRedirectOutput:
    """ class provides the get_output method for reading from a temporary file, and deletes it after that.
        the file creation is also managed here. However restoring stdout, stderr have to be done in the user class
    """
    def __init__(self,redirectop):
        self.op = None
        self.redirectop = redirectop

        self.tmpf = None
        if ( self.redirectop ):
            self.tmpf=tempfile.NamedTemporaryFile(suffix='.output',delete=False)
            self.old_stdout = sys.stdout
            self.old_stderr = sys.stderr
            sys.stdout = self.tmpf
            sys.stderr = self.tmpf
        pass
    
        
    
    def get_output( self ):
        """ read the output from tmpfile once and delete it. Use cached copy for later. Memoized. """ 
        if ( not isinstance(self.op,str) ):
            self.op = ""
            if ( self.redirectop ):
                with open(self.tmpf.name) as fp:
                    self.op = fp.read()
                os.unlink( self.tmpf.name )
                self.tmpf = None
        
        return self.op


class EzhilRedirectInputOutput(EzhilRedirectOutput):
    def __init__(self,input_file,redirectop):
        EzhilRedirectOutput.__init__(self,redirectop)
        self.old_stdin = sys.stdin
        self.stdin = open( input_file )
    

class EzhilFileExecuter(EzhilRedirectOutput):
    """ run on construction - build a Ezhil lexer/parser/runtime and execute the file pointed to by @files """
    def __init__(self,file_input,debug=False,redirectop=False):        
        EzhilRedirectOutput.__init__(self,redirectop)
        
        try:
            lexer = EzhilLex(file_input)
            if ( debug ): lexer.dump_tokens()        
            parse_eval = EzhilInterpreter( lexer, debug )
            parse_eval.parse()
            if ( debug ):  print("*"*60);  print(str(parse_eval))
            env = parse_eval.evaluate()
        except Exception as e:            
            print("exception ",str(e))
            raise e
        finally:
            if ( redirectop ):
                self.tmpf.close()
                sys.stdout = self.old_stdout
                sys.stderr = self.old_stderr
        

def local_REPL( file_input, lang, lexer, parse_eval, debug=False):    
    #refactor out REPL for ezhil and exprs
    env = None ## get the first instance from evaluate_interactive
    do_quit = False
        ## world-famous REPL
    with open(file_input) as fp:
        lines = fp.readlines()
    #lines = "\n".join([line.strip() for line in lines])
    totbuffer = ""
    max_lines = len(lines)
    for line_no,Lbuffer in enumerate(lines):        
        try:
            curr_line_no = "%s %d> "%(lang,line_no)
            Lbuffer = Lbuffer.strip()
            if ( Lbuffer == 'exit' ):
                do_quit = True
        except EOFError as e:
            print("End of Input reached\n")
            do_quit = True ##evaluate the Lbuffer             
        if ( debug ):
            print("evaluating buffer", Lbuffer)
            if ( len(totbuffer) > 0 ):
                print("tot buffer %s"%totbuffer) #debugging aid
            
        
        if ( do_quit ):
            print("******* வணக்கம்! பின்னர் உங்களை  பார்க்கலாம். *******") 
            return
        try:
            lexer.set_line_col([line_no, 0])
            if len(totbuffer) == 0:
                totbuffer = Lbuffer
            else:
                totbuffer += "\n"+ Lbuffer
            lexer.tokenize(totbuffer)
            [lexer_line_no,c] = lexer.get_line_col( 0 )
            if ( debug ): lexer.dump_tokens()
            try:
                if ( debug ): print ("parsing buffer item => ",totbuffer)
                parse_eval.parse()                
            except Exception as pexp:                
                ## clear tokens in lexer
                lexer.tokens = list()
                if ( debug ): print ("offending buffer item => ",totbuffer)
                if ( debug ): print(str(pexp),str(pexp.__class__))
                # Greedy strategy to keep avoiding parse-errors by accumulating more of input.
                # this allows a line-by-line execution strategy. When all else fails we report.
                if ( (line_no + 1) ==  max_lines ):
                    raise pexp
                continue
            totbuffer = ""
            sys.stdout.write(curr_line_no)
            if ( debug ):  print("*"*60);  print(str(parse_eval))
            [rval, env] = parse_eval.evaluate_interactive(env)
            if hasattr( rval, 'evaluate' ):
                print(rval.__str__())
            elif rval:
                print(rval)
            else:
                print("\n")
        except Exception as e:
            print(e)
            raise e
    return


class EzhilInterpExecuter(EzhilRedirectInputOutput):
    """ run on construction - build a Ezhil lexer/parser/runtime and execute the file pointed to by @files """
    def __init__(self,file_input,debug=False,redirectop=False):
        EzhilRedirectInputOutput.__init__(self,file_input,redirectop)
        
        try:
            lang = "எழில்"
            lexer = EzhilLex( )
            parse_eval = EzhilInterpreter( lexer, debug )
            local_REPL( file_input, lang, lexer, parse_eval, debug )
        except Exception as e:            
            print("exception ",str(e))
            raise e
        finally:
            if ( redirectop ):
                self.tmpf.close()
                sys.stdout = self.old_stdout
                sys.stderr = self.old_stderr
                sys.stdin = self.old_stdin

if __name__ == "__main__":
    lang = "எழில்"
    [fname, debug, dostdin ]= get_prog_name(lang)
    if ( dostdin ):
        ## interactive interpreter
        lexer = EzhilLex( )
        parse_eval = EzhilInterpreter( lexer, debug )
        REPL( lang, lexer, parse_eval, debug )
    else:
        ## evaluate a files sequentially
        for files in fname:
            EzhilFileExecuter( files )
    pass
