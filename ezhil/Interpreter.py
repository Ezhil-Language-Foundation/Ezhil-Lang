## -*- coding: utf-8 -*-
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

from ast import String, Number

## scanner for exprs language
from scanner import Token, Lexeme, Lex

## exceptions
from errors import RuntimeException, ParseException

## runtime elements
from runtime import  Environment, BuiltinFunction, \
 BlindBuiltins, DebugUtils

## builtins
import random

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

# program name
def get_prog_name(lang):
    prog_name=None
    debug=False
    
    # by-default look in the stdin
    if ( len(sys.argv) < 2 ):
        sys.argv.append( '-stdin' );
    
    if ( '--help' in sys.argv ):
        print "usage: %s.py {-stdin|filename} {-debug}"%(lang)
        sys.exit(-1)
    
    if ( len(sys.argv) >= 2 ):
        prog_name=sys.argv[1]
    
    if ( len(sys.argv) >= 3 ):
        debug = (sys.argv[2] == "-debug")
    return [prog_name, debug]

## Gandalf the Grey. One ring to rule them all.
class Interpreter(DebugUtils):
    """ when you add new language feature, add a AST class 
    and its evaluate methods. Also add a parser method """
    def __init__(self,lexer, dbg = False):
        DebugUtils.__init__(self,dbg)
        self.debug = dbg
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
        
        for b in dir(os):
            bfn = getattr( os ,b)
            self.add_blind_fcns( bfn, b)
        
        for b in dir(sys):
            bfn = getattr( sys ,b)
            self.add_blind_fcns( bfn, b)
    
    # marshalling
    @staticmethod
    def RAWINPUT(args):
        op = raw_input(args)
        return String(op)

    @staticmethod
    def INPUT(args):
        op = input(args)
        if ( isinstance(op,int) or isinstance(op,float) ):
            return Number(0.0+op)
        return String( op )
    
    def install_builtins(self):
        """ populate with the builtin functions"""

        self.builtin_map['abs']=BlindBuiltins(abs,'abs',self.debug)
        self.builtin_map['all']=BlindBuiltins(all,'all',self.debug)
        self.builtin_map['any']=BlindBuiltins(any,'any',self.debug)
        self.builtin_map['apply']=BlindBuiltins(apply,'apply',self.debug)
        self.builtin_map['basestring']=BlindBuiltins(basestring,'basestring',self.debug)
        self.builtin_map['bin']=BlindBuiltins(bin,'bin',self.debug)
        self.builtin_map['bool']=BlindBuiltins(bool,'bool',self.debug)
        self.builtin_map['buffer']=BlindBuiltins(buffer,'buffer',self.debug)
        self.builtin_map['bytearray']=BlindBuiltins(bytearray,'bytearray',self.debug)
        self.builtin_map['bytes']=BlindBuiltins(bytes,'bytes',self.debug)
        self.builtin_map['callable']=BlindBuiltins(callable,'callable',self.debug)
        self.builtin_map['chr']=BlindBuiltins(chr,'chr',self.debug)
        self.builtin_map['classmethod']=BlindBuiltins(classmethod,'classmethod',self.debug)
        self.builtin_map['cmp']=BlindBuiltins(cmp,'cmp',self.debug)
        self.builtin_map['coerce']=BlindBuiltins(coerce,'coerce',self.debug)
        self.builtin_map['compile']=BlindBuiltins(compile,'compile',self.debug)
        self.builtin_map['complex']=BlindBuiltins(complex,'complex',self.debug)
        self.builtin_map['copyright']=BlindBuiltins(copyright,'copyright',self.debug)
        self.builtin_map['credits']=BlindBuiltins(credits,'credits',self.debug)
        self.builtin_map['delattr']=BlindBuiltins(delattr,'delattr',self.debug)
        self.builtin_map['dict']=BlindBuiltins(dict,'dict',self.debug)
        self.builtin_map['dir']=BlindBuiltins(dir,'dir',self.debug)
        self.builtin_map['divmod']=BlindBuiltins(divmod,'divmod',self.debug)
        self.builtin_map['enumerate']=BlindBuiltins(enumerate,'enumerate',self.debug)
        self.builtin_map['eval']=BlindBuiltins(eval,'eval',self.debug)
        self.builtin_map['execfile']=BlindBuiltins(execfile,'execfile',self.debug)
        self.builtin_map['exit']=BlindBuiltins(exit,'exit',self.debug)
        self.builtin_map['file']=BlindBuiltins(file,'file',self.debug)
        self.builtin_map['filter']=BlindBuiltins(filter,'filter',self.debug)
        self.builtin_map['float']=BlindBuiltins(float,'float',self.debug)
        self.builtin_map['format']=BlindBuiltins(format,'format',self.debug)
        self.builtin_map['frozenset']=BlindBuiltins(frozenset,'frozenset',self.debug)
        self.builtin_map['getattr']=BlindBuiltins(getattr,'getattr',self.debug)
        self.builtin_map['globals']=BlindBuiltins(globals,'globals',self.debug)
        self.builtin_map['hasattr']=BlindBuiltins(hasattr,'hasattr',self.debug)
        self.builtin_map['hash']=BlindBuiltins(hash,'hash',self.debug)
        self.builtin_map['help']=BlindBuiltins(help,'help',self.debug)
        self.builtin_map['hex']=BlindBuiltins(hex,'hex',self.debug)
        self.builtin_map['id']=BlindBuiltins(id,'id',self.debug)
        self.builtin_map['input']=BlindBuiltins(input,'input',self.debug)
        self.builtin_map['int']=BlindBuiltins(int,'int',self.debug)
        self.builtin_map['intern']=BlindBuiltins(intern,'intern',self.debug)
        self.builtin_map['isinstance']=BlindBuiltins(isinstance,'isinstance',self.debug)
        self.builtin_map['issubclass']=BlindBuiltins(issubclass,'issubclass',self.debug)
        self.builtin_map['iter']=BlindBuiltins(iter,'iter',self.debug)
        self.builtin_map['len']=BlindBuiltins(len,'len',self.debug)
        self.builtin_map['license']=BlindBuiltins(license,'license',self.debug)
        self.builtin_map['list']=BlindBuiltins(list,'list',self.debug)
        self.builtin_map['locals']=BlindBuiltins(locals,'locals',self.debug)
        self.builtin_map['long']=BlindBuiltins(long,'long',self.debug)
        self.builtin_map['map']=BlindBuiltins(map,'map',self.debug)
        self.builtin_map['max']=BlindBuiltins(max,'max',self.debug)
        self.builtin_map['memoryview']=BlindBuiltins(memoryview,'memoryview',self.debug)
        self.builtin_map['min']=BlindBuiltins(min,'min',self.debug)
        self.builtin_map['next']=BlindBuiltins(next,'next',self.debug)
        self.builtin_map['object']=BlindBuiltins(object,'object',self.debug)
        self.builtin_map['oct']=BlindBuiltins(oct,'oct',self.debug)
        self.builtin_map['open']=BlindBuiltins(open,'open',self.debug)
        self.builtin_map['ord']=BlindBuiltins(ord,'ord',self.debug)
        self.builtin_map['pow']=BlindBuiltins(pow,'pow',self.debug)
        self.builtin_map['property']=BlindBuiltins(property,'property',self.debug)
        self.builtin_map['quit']=BlindBuiltins(quit,'quit',self.debug)
        self.builtin_map['range']=BlindBuiltins(range,'range',self.debug)
        self.builtin_map['raw_input']=BlindBuiltins(raw_input,'raw_input',self.debug)
        self.builtin_map['reduce']=BlindBuiltins(reduce,'reduce',self.debug)
        self.builtin_map['reload']=BlindBuiltins(reload,'reload',self.debug)
        self.builtin_map['repr']=BlindBuiltins(repr,'repr',self.debug)
        self.builtin_map['reversed']=BlindBuiltins(reversed,'reversed',self.debug)
        self.builtin_map['round']=BlindBuiltins(round,'round',self.debug)
        self.builtin_map['set']=BlindBuiltins(set,'set',self.debug)
        self.builtin_map['setattr']=BlindBuiltins(setattr,'setattr',self.debug)
        self.builtin_map['slice']=BlindBuiltins(slice,'slice',self.debug)
        self.builtin_map['sorted']=BlindBuiltins(sorted,'sorted',self.debug)
        self.builtin_map['staticmethod']=BlindBuiltins(staticmethod,'staticmethod',self.debug)
        self.builtin_map['str']=BlindBuiltins(str,'str',self.debug)
        self.builtin_map['sum']=BlindBuiltins(sum,'sum',self.debug)
        self.builtin_map['super']=BlindBuiltins(super,'super',self.debug)
        self.builtin_map['tuple']=BlindBuiltins(tuple,'tuple',self.debug)
        self.builtin_map['type']=BlindBuiltins(type,'type',self.debug)
        self.builtin_map['unichr']=BlindBuiltins(unichr,'unichr',self.debug)
        self.builtin_map['unicode']=BlindBuiltins(unicode,'unicode',self.debug)
        self.builtin_map['vars']=BlindBuiltins(vars,'vars',self.debug)
        self.builtin_map['xrange']=BlindBuiltins(xrange,'xrange',self.debug)
        self.builtin_map['zip']=BlindBuiltins(zip,'zip',self.debug)

        # input statements
        self.builtin_map["input"]=BuiltinFunction(Interpreter.INPUT,"input")
        self.builtin_map["raw_input"]=BuiltinFunction(Interpreter.RAWINPUT,"raw_input")

        # assert
        self.builtin_map["assert"]=BuiltinFunction(lambda x: x and True or Exception('Assertion failed!'),"assert")
        
        # random functions
        aslist = True;
        self.builtin_map["choice"]=BlindBuiltins(random.choice,"choice",self.debug,aslist)
        self.builtin_map["random"]=BuiltinFunction(random.random,"random",0)
        self.builtin_map["seed"]=BuiltinFunction(random.seed,"seed")
        self.builtin_map["randint"]=BuiltinFunction(random.randint,"randint",2)
        
        # math functions
        self.builtin_map["acos"]=BuiltinFunction(acos,"acos")
        self.builtin_map["asin"]=BuiltinFunction(asin,"asin")
        self.builtin_map["atan"]=BuiltinFunction(atan,"atan")
        self.builtin_map["atan2"]=BuiltinFunction(atan2,"atan2")
        self.builtin_map["ceil"]=BuiltinFunction(ceil,"ceil")
        self.builtin_map["cos"]=BuiltinFunction(cos,"cos")
        self.builtin_map["cosh"]=BuiltinFunction(cosh,"cosh")
        self.builtin_map["degrees"]=BuiltinFunction(degrees,"degrees")
        self.builtin_map["e"]=BuiltinFunction(lambda : e,"e",0)
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
        self.builtin_map["pi"]=BuiltinFunction(lambda : pi,"pi",0)
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
                do_quit = True
        except EOFError, e:
            print "End of Input reached\n"
            do_quit = True ##evaluate the buffer 
            ## line-no broke
        if ( debug ): print "evaluating buffer", buffer
        if ( do_quit ):
            if ( lang == 'ezhil' ):
                print "******* வணக்கம்! பின்னர் உங்களை  பார்க்கலாம். *******" 
            else:
                print "******* Goodbye! Now have a nice day *******" 
            sys.exit( 0 )
        try:
            lexer.set_line_col([line_no, 0])
            lexer.tokenize(buffer)
            [line_no,c] = lexer.get_line_col( 0 )
            if ( debug ): lexer.dump_tokens()
            parse_eval.parse()
            if ( debug ):  print "*"*60;  print str(parse_eval)
            [rval, env] = parse_eval.evaluate_interactive(env)
            if rval:
                if hasattr( rval, 'evaluate' ):
                    rval.evaluate(env)
                else:
                    print rval
        except Exception, e:
            print e
            ## clear tokens in lexer
            lexer.tokens = list()
        
    return
