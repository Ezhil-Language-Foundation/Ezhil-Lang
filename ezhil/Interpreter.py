## -*- coding: UTF-8 -*-
## (C) 2007, 2008, 2013 Muthiah Annamalai,
## Licensed under GPL Version 3
##
## 1/25/08: move the scanner outside to another module.
##          REPL-interpreter
## 1/24/08: add Lexer line,col,file information.
## 1/22/08: fix division operator, and function eval. add while.
## 1/21/08: add newer operators.
## 1/20/08: new lexer, and fix some evaluation errors.
## 1/16/08: add bulitin functions. make space for conditionals.
## 1/15/08: add simple function support.
## 1/08/08: add visitor pattern to AST Objects.
## 
## FEATURES: add array / list syntax.
## TODO: extract scanner and AST members into a module for sharing.
## FIXME: grammar for expression maybe broke. precedence.

from math import *
import copy
import os, sys, string, inspect

## scanner for exprs language
from scanner import Token, Lexeme, Lex

## exceptions
from errors import RuntimeException, ParseException

## runtime elements
from runtime import  Environment, BuiltinFunction, \
 BlindBuiltins, DebugUtils

## AST elements
from ast import Expr, ExprCall, ExprList, Stmt, ReturnStmt, \
 BreakStmt, ContinueStmt, ElseStmt, IfStmt, WhileStmt, \
 ForStmt, AssignStmt, PrintStmt, EvalStmt, ArgList, \
 ValueList, Function, StmtList, Identifier, Number, \
 String

## Parser
from parser import Parser

## Transform / Visitor
from transform import TreeWalker

## Gandalf the Grey. One ring to rule them all.
class Interpreter(DebugUtils):
    """ when you add new language feature, add a AST class 
    and its evaluate methods. Also add a parser method """
    def __init__(self,lexer, dbg = False):
        DebugUtils.__init__(self,dbg)
        self.lexer=lexer
        self.ast=None
        self.function_map = dict()#parsed functions
        self.builtin_map = dict() #pointers to builtin functions
        self.call_stack = list() #call stack
        
        ## use the default Exprs parser.
        lang_parser = Parser(self.lexer,self.function_map, \
                             self.builtin_map, self.debug )
        self.parser = lang_parser

        ## run the installation code last
        self.install_builtins()
        self.install_blind_builtins()

    def change_parser(self,parser_ctor):
        """ change the parser to your-cool-language using
         a lambda function parser_ctor the constructor """
        lang_parser = parser_ctor(self.lexer,self.function_map, \
                             self.builtin_map, self.debug )
        self.parser = lang_parser
        return True

    def add_blind_fcns(self, bfn, b):
        """ an internal method to reduce repetition """
        if ( not inspect.ismethod(bfn) 
             and not inspect.isclass(bfn)
             and callable(bfn) ):
            self.dbg_msg("adding: "+b);
            self.builtin_map[b] = BlindBuiltins( bfn, b);
        else:
            self.dbg_msg("skipping: "+b);
        return

    def install_blind_builtins(self):
        """ we dont know the arity of these functions,
        hence we call-em the blind builtins, but we 
        still add them to the builtin_map """

        for b in dir(__builtins__):
            bfn = getattr( __builtins__ ,b)
            self.add_blind_fcns( bfn , b )

        for b in dir(os):
            bfn = getattr( os ,b)
            self.add_blind_fcns( bfn, b)

        for b in dir(__builtins__):
            bfn = getattr( __builtins__ ,b)
            self.add_blind_fcns( bfn , b )

        for b in dir(sys):
            bfn = getattr( sys ,b)
            self.add_blind_fcns( bfn, b)
            
            
        
    def install_builtins(self):
        """ populate with the builtin functions"""
        self.builtin_map["acos"]=BuiltinFunction(acos,"acos")
        self.builtin_map["asin"]=BuiltinFunction(asin,"asin")
        self.builtin_map["atan"]=BuiltinFunction(atan,"atan")
        self.builtin_map["atan2"]=BuiltinFunction(atan2,"atan2")
        self.builtin_map["ceil"]=BuiltinFunction(ceil,"ceil")
        self.builtin_map["cos"]=BuiltinFunction(cos,"cos")
        self.builtin_map["cosh"]=BuiltinFunction(cosh,"cosh")
        self.builtin_map["degrees"]=BuiltinFunction(degrees,"degrees")
        self.builtin_map["e"]=BuiltinFunction(e,"e")
        self.builtin_map["exp"]=BuiltinFunction(exp,"exp")
        self.builtin_map["fabs"]=BuiltinFunction(fabs,"fabs")
        self.builtin_map["floor"]=BuiltinFunction(floor,"floor")
        self.builtin_map["fmod"]=BuiltinFunction(fmod,"fmod",2)
        self.builtin_map["frexp"]=BuiltinFunction(frexp,"frexp")
        self.builtin_map["hypot"]=BuiltinFunction(hypot,"hypot",2)
        self.builtin_map["ldexp"]=BuiltinFunction(ldexp,"ldexp")
        self.builtin_map["log"]=BuiltinFunction(log,"log")
        self.builtin_map["log10"]=BuiltinFunction(log10,"log10")
        self.builtin_map["modf"]=BuiltinFunction(modf,"modf",2)
        self.builtin_map["pi"]=BuiltinFunction(pi,"pi",0)
        self.builtin_map["pow"]=BuiltinFunction(pow,"pow",2)
        self.builtin_map["radians"]=BuiltinFunction(radians,"radians")
        self.builtin_map["sin"]=BuiltinFunction(sin,"sin")
        self.builtin_map["sinh"]=BuiltinFunction(sinh,"sinh")
        self.builtin_map["sqrt"]=BuiltinFunction(sqrt,"sqrt")
        self.builtin_map["tan"]=BuiltinFunction(tan,"tan")
        self.builtin_map["tanh"]=BuiltinFunction(tanh,"tanh")

        self.builtin_map["max"]=BuiltinFunction(max,"max",2)
        self.builtin_map["min"]=BuiltinFunction(min,"min",2)
        self.builtin_map["exit"]=BuiltinFunction(min,"exit",1)
        return True

    def __repr__(self):
        rval =  "[Interpreter: "
        rval = rval + "[Functions["
        for k in self.function_map.keys():
            rval = rval + "\n "+ str(self.function_map[k]) 
        rval = rval +"]] "+ str(self.ast) +"]\n"
        return rval

    def parse(self):
        """ parser routine """
        self.ast = self.parser.parse()
        return self.ast

    def evaluate(self):
        env = Environment( self.call_stack, self.function_map, \
                               self.builtin_map, self.debug )
        env.call_function("__toplevel__") ##some context
        return self.ast.evaluate(env)

    def evaluate_interactive(self,env = None):
        ## use a persistent environment for interactive interpreter
        if ( not env ):
            env = Environment( self.call_stack, self.function_map, \
                                   self.builtin_map, self.debug )
            env.call_function("__toplevel__") ##some context
        ## use this from the interactive-interpreter
        rval = self.ast.evaluate(env)
        return [ rval, env ]

def REPL(lang, lexer, parse_eval, debug=False):    
    #refactor out REPL for ezhil and exprs
    env = None ## get the first instance from evaluate_interactive
    line_no = 1
    do_quit = False
        ## world-famous REPL
    while not sys.stdin.closed :
        try:
            print "%s %d> "%(lang,line_no),
                ## FIXME: implement multiple line readline library
            buffer = sys.stdin.readline();
            buffer = buffer.strip()
            line_no += 1
            if ( buffer == 'exit' ):
                sys.exit(0)
        except EOFError, e:
            print "End of Input reached\n"
            do_quit = True ##evaluate the buffer 
            ## line-no broke
        print "evaluating buffer", buffer
        try:
            lexer.set_line_col([line_no, 0])
            lexer.tokenize(buffer)
            [line_no,c] = lexer.get_line_col( 0 )
            if ( debug ): lexer.dump_tokens()
            parse_eval.parse()
            if ( debug ):  print "*"*60;  print str(parse_eval)
            [rval, env] = parse_eval.evaluate_interactive(env)
            if rval : print rval
        except Exception, e:
            print e
            ## clear tokens in lexer
            lexer.tokens = list()
        
        if ( do_quit ):
            if ( lang == 'ezhil' ):
                print "******* வணக்கம்! பின்னர் உங்களை  பார்க்கலாம். *******" 
            else:
                print "******* Goodbye! Now have a nice day *******" 
            sys.exit( 0 )

    return
