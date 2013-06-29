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
import argparse
from math import *
import copy
import os, sys, string, inspect
import string

from ast import String, Number

## scanner for exprs language
from scanner import Token, Lexeme, Lex

## exceptions
from errors import RuntimeException, ParseException

## runtime elements
from runtime import  Environment, BuiltinFunction, \
 BlindBuiltins, DebugUtils

# turtle graphics
from EZTurtle import EZTurtle

## builtins
import random

## AST elements
from ast import Expr, ExprCall, ExprList, Stmt, ReturnStmt, \
 BreakStmt, ContinueStmt, ElseStmt, IfStmt, WhileStmt, \
 ForStmt, AssignStmt, PrintStmt, EvalStmt, ArgList, \
 ValueList, Function, StmtList, Identifier, Number, \
 String

## Parser
from ExprsParser import Parser

## Transform / Visitor
from transform import TreeWalker
import collections

def ezhil_copyright():
	return "(C) 2007-2013 Muthiah Annamalai"

# you can also, get your name here, its easy!
def ezhil_credits():
	return "Ezhil language was created by Muthiah Annamalai in 2007-2008"

def ezhil_license():
	return "Licensed under GPL Version 3"

# program name
def get_prog_name(lang):
    prog_name=None
    debug=False
    
    parser = argparse.ArgumentParser(prog=lang)
    parser.add_argument("files",nargs='*',default=[])
    parser.add_argument("-debug",action="store_true",
                        default=False,
                        help="enable debugging information on screen")
    parser.add_argument("-stdin",action="store_true",
                        default=None,
                        help="read input from the standard input")
    args = parser.parse_args()
    
    if len(args.files) == 0 and (not args.stdin):
        parser.print_help()
        sys.exit(-1)
    
    prog_name = args.files
    debug = args.debug
    dostdin = args.stdin
    
    return [prog_name, debug, dostdin]

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
             and isinstance(bfn, collections.Callable) ):
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
        op = eval(input(args))
        if ( isinstance(op,int) or isinstance(op,float) ):
            return Number(0.0+op)
        return String( op )

    @staticmethod   
    def SPRINTF_worker(*args):        
        if ( len(args) < 1 ):
            raise Exception('Not enough arguments to printf() function')
        fmt = args[0]
        arg = tuple( args[1:] );
        opstr = fmt%arg;
        return opstr

    @staticmethod
    def SPRINTF(*args):
        opstr = Interpreter.SPRINTF_worker(*args);
        return String(opstr)
    
    @staticmethod   
    def PRINTF(*args):
        str_op = Interpreter.SPRINTF_worker(*args);
        print(str_op)
        return Number(len(str_op))
    
    def install_builtins(self):
        """ populate with the builtin functions"""
        self.builtin_map['printf']=BlindBuiltins(Interpreter.PRINTF,'printf',self.debug)
        self.builtin_map['sprintf']=BlindBuiltins(Interpreter.SPRINTF,'sprintf',self.debug)
        
        self.builtin_map['abs']=BlindBuiltins(abs,'abs',self.debug)
        self.builtin_map['all']=BlindBuiltins(all,'all',self.debug)
        self.builtin_map['any']=BlindBuiltins(any,'any',self.debug)
        self.builtin_map['apply']=BlindBuiltins(apply,'apply',self.debug)
        self.builtin_map['basestring']=BlindBuiltins(str,'basestring',self.debug)
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
        self.builtin_map['copyright']=BlindBuiltins(ezhil_copyright,'copyright',self.debug)
        self.builtin_map['credits']=BlindBuiltins(ezhil_credits,'credits',self.debug)
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
        #self.builtin_map['input']=BlindBuiltins(input,'input',self.debug)
        self.builtin_map['int']=BlindBuiltins(int,'int',self.debug)
        self.builtin_map['intern']=BlindBuiltins(intern,'intern',self.debug)
        self.builtin_map['isinstance']=BlindBuiltins(isinstance,'isinstance',self.debug)
        self.builtin_map['issubclass']=BlindBuiltins(issubclass,'issubclass',self.debug)
        self.builtin_map['iter']=BlindBuiltins(iter,'iter',self.debug)
        self.builtin_map['len']=BlindBuiltins(len,'len',self.debug)
        self.builtin_map['license']=BlindBuiltins(ezhil_license,'license',self.debug)
        #self.builtin_map['list']=BlindBuiltins(list,'list',self.debug)
        #self.builtin_map['locals']=BlindBuiltins(locals,'locals',self.debug)
        self.builtin_map['long']=BlindBuiltins(int,'long',self.debug)
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
        #self.builtin_map['raw_input']=BlindBuiltins(raw_input,'raw_input',self.debug)
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
        self.builtin_map['unichr']=BlindBuiltins(chr,'unichr',self.debug)
        self.builtin_map['unicode']=BlindBuiltins(str,'unicode',self.debug)
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

        # turtle functions
        turtle_attrib = EZTurtle.functionAttributes();
        for nargs,fcnName in list(turtle_attrib.items()):
            for vv in fcnName:
                turtlefcn = "turtle_"+vv;
                if ( self.debug ): print(nargs, vv)
                if ( nargs == -1 ):
                    self.builtin_map[turtlefcn] = BlindBuiltins(getattr(EZTurtle, vv),vv,self.debug)
                else:
                    self.builtin_map[turtlefcn] = BuiltinFunction( getattr( EZTurtle, vv ), turtlefcn, nargs )
        
        #string functions
#       for x in dir(string):
#            if ( x.__str__()[0] != '_' ):
#                name = x.__str__()
#                print "self.builtin_map[\"%s\"] = BuiltinFunction(getattr(string,\"%s\"),\"%s\")"%(name,name,name)
        
        self.builtin_map["ascii_letters"] = BuiltinFunction(getattr(string,"ascii_letters"),"ascii_letters",0)
        self.builtin_map["ascii_lowercase"] = BuiltinFunction(getattr(string,"ascii_lowercase"),"ascii_lowercase",0)
        self.builtin_map["ascii_uppercase"] = BuiltinFunction(getattr(string,"ascii_uppercase"),"ascii_uppercase",0)
        self.builtin_map["atof"] = BuiltinFunction(getattr(string,"atof"),"atof")
        self.builtin_map["atof_error"] = BuiltinFunction(getattr(string,"atof_error"),"atof_error")
        self.builtin_map["atoi"] = BuiltinFunction(getattr(string,"atoi"),"atoi")
        self.builtin_map["atoi_error"] = BuiltinFunction(getattr(string,"atoi_error"),"atoi_error")
        self.builtin_map["atol"] = BuiltinFunction(getattr(string,"atol"),"atol")
        self.builtin_map["atol_error"] = BuiltinFunction(getattr(string,"atol_error"),"atol_error")
        self.builtin_map["capitalize"] = BuiltinFunction(getattr(string,"capitalize"),"capitalize")
        self.builtin_map["capwords"] = BuiltinFunction(getattr(string,"capwords"),"capwords")
        self.builtin_map["center"] = BuiltinFunction(getattr(string,"center"),"center")
        self.builtin_map["count"] = BuiltinFunction(getattr(string,"count"),"count")
        self.builtin_map["digits"] = BuiltinFunction(getattr(string,"digits"),"digits")
        self.builtin_map["expandtabs"] = BuiltinFunction(getattr(string,"expandtabs"),"expandtabs")
        self.builtin_map["find"] = BuiltinFunction(getattr(string,"find"),"find",2)
        self.builtin_map["hexdigits"] = BuiltinFunction(getattr(string,"hexdigits"),"hexdigits")
        self.builtin_map["index"] = BuiltinFunction(getattr(string,"index"),"index",2)
        self.builtin_map["index_error"] = BuiltinFunction(getattr(string,"index_error"),"index_error")
        self.builtin_map["join"] = BuiltinFunction(getattr(string,"join"),"join")
        self.builtin_map["joinfields"] = BuiltinFunction(getattr(string,"joinfields"),"joinfields")
        self.builtin_map["letters"] = BuiltinFunction(getattr(string,"letters"),"letters")
        self.builtin_map["ljust"] = BuiltinFunction(getattr(string,"ljust"),"ljust")
        self.builtin_map["lower"] = BuiltinFunction(getattr(string,"lower"),"lower")
        self.builtin_map["lowercase"] = BuiltinFunction(getattr(string,"lowercase"),"lowercase")
        self.builtin_map["lstrip"] = BuiltinFunction(getattr(string,"lstrip"),"lstrip")
        self.builtin_map["maketrans"] = BuiltinFunction(getattr(string,"maketrans"),"maketrans")
        self.builtin_map["octdigits"] = BuiltinFunction(getattr(string,"octdigits"),"octdigits")
        self.builtin_map["printable"] = BuiltinFunction(getattr(string,"printable"),"printable")
        self.builtin_map["punctuation"] = BuiltinFunction(getattr(string,"punctuation"),"punctuation")
        self.builtin_map["replace"] = BuiltinFunction(getattr(string,"replace"),"replace",3)
        self.builtin_map["rfind"] = BuiltinFunction(getattr(string,"rfind"),"rfind",2)
        self.builtin_map["rindex"] = BuiltinFunction(getattr(string,"rindex"),"rindex",2)
        self.builtin_map["rjust"] = BuiltinFunction(getattr(string,"rjust"),"rjust")
        self.builtin_map["rsplit"] = BuiltinFunction(getattr(string,"rsplit"),"rsplit")
        self.builtin_map["rstrip"] = BuiltinFunction(getattr(string,"rstrip"),"rstrip")
        self.builtin_map["split"] = BuiltinFunction(getattr(string,"split"),"split",2)
        self.builtin_map["splitfields"] = BuiltinFunction(getattr(string,"splitfields"),"splitfields")
        self.builtin_map["strip"] = BuiltinFunction(getattr(string,"strip"),"strip")
        self.builtin_map["swapcase"] = BuiltinFunction(getattr(string,"swapcase"),"swapcase")
        self.builtin_map["translate"] = BuiltinFunction(getattr(string,"translate"),"translate")
        self.builtin_map["upper"] = BuiltinFunction(getattr(string,"upper"),"upper")
        self.builtin_map["uppercase"] = BuiltinFunction(getattr(string,"uppercase"),"uppercase")
        self.builtin_map["whitespace"] = BuiltinFunction(getattr(string,"whitespace"),"whitespace")
        self.builtin_map["zfill"] = BuiltinFunction(getattr(string,"zfill"),"zfill",2)

        #add list methods - first argument, when required, is always a list obj
        self.builtin_map["append"] = BuiltinFunction(list.append,"append",2)
        self.builtin_map["insert"] = BuiltinFunction(list.insert,"insert",3)
        self.builtin_map["index"] = BuiltinFunction(list.index,"index",2)
        self.builtin_map["list"] = BuiltinFunction(list,"list",0)
        self.builtin_map["pop"] = BuiltinFunction(list.pop,"pop",1)
        self.builtin_map["sort"] = BuiltinFunction(list.sort,"sort",1)
        self.builtin_map["count"]= BuiltinFunction(list.count,"count",2)
        self.builtin_map["extend"]= BuiltinFunction(list.extend,"extend",2)
        self.builtin_map["reverse"]= BuiltinFunction(list.reverse,"reverse",1)
        self.builtin_map["get"]= BuiltinFunction(list.__getitem__,"get",2)
        
        # #dictionary methods - 
        # self.builtin_map["clear"]= BuiltinFunction(dict.clear,"clear",1)
        # self.builtin_map["copy"]= BuiltinFunction(dict.copy,"copy",1)
        # self.builtin_map["fromkeys"]= BuiltinFunction(dict.fromkeys,"fromkeys",1)
        # self.builtin_map["get"]= BuiltinFunction(dict.get,"get",1)
        # self.builtin_map["has_key"]= BuiltinFunction(dict.has_key,"has_key",1)
        # self.builtin_map["items"]= BuiltinFunction(dict.items,"items",1)
        # self.builtin_map["iteritems"]= BuiltinFunction(dict.iteritems,"iteritems",1)
        # self.builtin_map["iterkeys"]= BuiltinFunction(dict.iterkeys,"iterkeys",1)
        # self.builtin_map["itervalues"]= BuiltinFunction(dict.itervalues,"itervalues",1)
        # self.builtin_map["keys"]= BuiltinFunction(dict.keys,"keys",1)
        # self.builtin_map["pop"]= BuiltinFunction(dict.pop,"pop",1)
        # self.builtin_map["popitem"]= BuiltinFunction(dict.popitem,"popitem",1)
        # self.builtin_map["setdefault"]= BuiltinFunction(dict.setdefault,"setdefault",1)
        # self.builtin_map["update"]= BuiltinFunction(dict.update,"update",1)
        # self.builtin_map["values"]= BuiltinFunction(dict.values,"values",1)
        # self.builtin_map["viewitems"]= BuiltinFunction(dict.viewitems,"viewitems",1)
        # self.builtin_map["viewkeys"]= BuiltinFunction(dict.viewkeys,"viewkeys",1)
        # self.builtin_map["viewvalues"]= BuiltinFunction(dict.viewvalues,"viewvalues",1)

        return True

    def __repr__(self):
        rval =  "[Interpreter: "
        rval = rval + "[Functions["
        for k in list(self.function_map.keys()):
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
            sys.stdout.write("%s %d> "%(lang,line_no))
            ## FIXME: implement multiple line readline library
            buffer = sys.stdin.readline();
            buffer = buffer.strip()
            line_no += 1
            if ( buffer.strip() == 'exit' ):
                do_quit = True
        except EOFError as e:
            print("End of Input reached\n")
            do_quit = True ##evaluate the buffer 
            ## line-no broke
        if ( debug ): print("evaluating buffer", buffer)
        if ( do_quit ):
            if ( lang == 'ezhil' ):
                print("******* வணக்கம்! பின்னர் உங்களை  பார்க்கலாம். *******") 
            else:
                print("******* Goodbye! Now have a nice day *******") 
            sys.exit( 0 )
        try:
            lexer.set_line_col([line_no, 0])
            lexer.tokenize(buffer)
            [line_no,c] = lexer.get_line_col( 0 )
            if ( debug ): lexer.dump_tokens()
            parse_eval.parse()
            if ( debug ):  print("*"*60);  print(str(parse_eval))
            [rval, env] = parse_eval.evaluate_interactive(env)
            if hasattr( rval, 'evaluate' ):
                print(rval.__str__())
            else:
                print(rval)
        except Exception as e:
            print(e)
            ## clear tokens in lexer
            lexer.tokens = list()
        
    return
