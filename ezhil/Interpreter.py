## -*- coding: utf-8 -*-
## (C) 2007, 2008, 2013, 2014, 2015 Muthiah Annamalai,
## Licensed under GPL Version 3
##
## 
## TODO: extract scanner and AST members into a module for sharing.
from __future__ import print_function

import argparse
from math import *
import copy, codecs
import os, sys, string, inspect
import string
import tamil
from cmd import Cmd
from pprint import pprint
import time

PYTHON3 = (sys.version[0] == '3')

ezhil_sleep = time.sleep
ezhil_date_time = time.asctime

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
 String, Boolean

## Parser
from ExprsParser import Parser

## Transform / Visitor
from transform import Visitor
import collections

def ezhil_version():
        return 0.76

def ezhil_copyright():
    return u"(C) 2007-2013 Muthiah Annamalai"

# you can also, get your name here, its easy!
def ezhil_credits():
    return u"Ezhil language, version %g, was created by Muthiah Annamalai in 2007-2008, and actively maintained in 2015."%(ezhil_version())

def ezhil_license():
    return u"Licensed under GPL Version 3"

def ezhil_tamil_length(arg):
	return Number( len( tamil.get_letters( arg ) ) )

def ezhil_getitem(*args):
    if len(args) < 2:
       raise Exception("getitem - too-few arguments, 2 or 3 arguments expected")
    with_default = (len(args) == 3)
    x = args[0]
    idx = args[1]
    if with_default:
        idxs = [idx,args[2]]
    else:
        idxs = [idx]
    #print("dispatching ezhil getitem",type(x),type(idx),x,idx,x[idx])
    if ( isinstance(x,dict) ):
        return x.get(*idxs)
    elif ( isinstance(x,list) or hasattr( x, '__getitem__') ):
        return x.__getitem__(*idxs)
    return x.__getitem__(*idxs)

def ezhil_islist( x ):
    return Boolean(isinstance(x,list))

def ezhil_isnumber( x ):
    return Boolean(isinstance(x,Number) or type(x) in [int, float] )

def ezhil_setitem(x,key,val):
    #print("dispatching ezhil setitem",type(x),type(idx),x,idx,x[idx])
    if ( isinstance(x,dict) or isinstance(x,list) or hasattr( x, '__setitem__') ):
        x.__setitem__(key,val)
    else:    
        x[key]=val
    return

def ezhil_load(filename):
    # load the file into the interpreter
    # we have a symbol table and use it
    pass

class NoClobberDict(dict):
    """ dictionary structure with a set like mathematical structure.
        that way when you insert functions for ezhil library, we don't trample on each other
        by accidentally overwriting stuff"""
    def __init__(self):
        dict.__init__(self)
    def __setitem__(self,key,val):
        if ( self.get(key,None) ):
            raise KeyError("Dictionary is getting clobbered; key "+key+" already present")
        dict.__setitem__(self,key,val)

global_interpreter = None

def ezhil_list_functions(*args):
    global global_interpreter
    global_interpreter.list_functions(*args)
    

## Gandalf the Grey. One ring to rule them all.
class Interpreter(DebugUtils):
    """ when you add new language feature, add a AST class 
    and its evaluate methods. Also add a parser method """
    def __init__(self,lexer, dbg = False,safe_mode=True):
        DebugUtils.__init__(self,dbg)
        self.SAFE_MODE = safe_mode
        self.debug = dbg
        self.MAX_REC_DEPTH = 10000
        self.lexer=lexer
        self.ast=None
        self.function_map = NoClobberDict()#parsed functions
        self.builtin_map = NoClobberDict() #pointers to builtin functions
        self.call_stack = list() #call stack
        sys.setrecursionlimit( self.MAX_REC_DEPTH ) # have a large enough Python stack        
        ## use the default Exprs parser.
        lang_parser = Parser(self.lexer,self.function_map, \
                             self.builtin_map, self.debug )
        self.parser = lang_parser
        
        ## run the installation code last
        self.install_builtins()
        self.install_blind_builtins()
        
        ## update globals
        global global_interpreter
        global_interpreter = self
        
        
    def reset(self):
        """ reset lexer and parser """
        self.parser.reset()
        self.lexer.reset()
        return

    def change_parser(self,parser_ctor):
        """ change the parser to your-cool-language using
         a lambda function parser_ctor the constructor """
        lang_parser = parser_ctor(self.lexer,self.function_map, \
                             self.builtin_map, self.debug )
        self.parser = lang_parser
        return True
    
    def list_functions(self,*args):
        if ( not args ):
            user_prefix = None
        else:
            user_prefix = args[0]
                
        print(u"######### Builtin Function ########")
        pos = 0
        for xpos,fcn in enumerate(self.builtin_map.keys()):
            if ( user_prefix and not fcn.startswith(user_prefix) ):
                continue
            pos = pos + 1
            print(u"%03d> %s"%(pos,unicode(fcn)))
        
        print(u"######### Functions - Library + User defined - ########")
        pos = 0
        for xpos,fcn in enumerate(self.function_map.keys()):
            if ( user_prefix and not fcn.startswith(user_prefix) ):
                continue
            pos = pos + 1
            print(u"%03d> %s"%(pos,unicode(fcn)))
        
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
            if self.SAFE_MODE:
                break
            bfn = getattr( os ,b)
            if str(b).find('exec') >= 0 or str(b).find('spawn') >= 0:
                continue
            self.add_blind_fcns( bfn, b)
        
        for b in dir(sys):
            bfn = getattr( sys ,b)
            self.add_blind_fcns( bfn, b)
    
    @staticmethod
    def ezhil_assert( x  ):
        # we raise Exception(u'Assertion failed!') further up stack
        assert x
        return True
    
    # file IO functions - 6 total
    @staticmethod
    def file_open(*args):
        args = list(args)
        if ( len(args) < 2 ):
                args.append('r') #default op = read
        if ( len(args) < 3 ):
                args.append('utf-8') #default encoding = utf-8
        fp = codecs.open(*args)
        return fp
    
    @staticmethod
    def file_close(*args):
        assert( len(args) == 1 )
        assert( hasattr(args[0],'close') )
        args[0].close()
        return
    
    @staticmethod
    def file_read(*args):
        assert( len(args) == 1 )
        assert( hasattr(args[0],'read') )
        return String( args[0].read() )
    
    @staticmethod
    def file_readlines(*args):
        assert( len(args) == 1 )
        assert( hasattr(args[0],'readlines') )
        return args[0].readlines()

    @staticmethod
    def file_write(*args):
        assert( len(args) == 2 )
        assert( hasattr(args[0],'write') )
        return args[0].write( args[1] )
    
    @staticmethod
    def file_writelines(*args):
        assert( len(args) == 2 )
        assert( hasattr(args[0],'writelines') )
        return args[0].writelines(args[1])
    
    # marshalling            
    @staticmethod
    def RAWINPUT(args):
        op = raw_input(args)
        return String(op)
    
    @staticmethod
    def INPUT(args):
        op = (raw_input(args))
        if ( isinstance(op,int) or isinstance(op,float) ):
            return Number(0.0+op)
        return String( op )
    
    @staticmethod   
    def SPRINTF_worker(*args):
        if ( len(args) < 1 ):
            raise Exception(u'Not enough arguments to printf() function')
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
    
    @staticmethod
    def ezhil_reverse(*args):
       if ( len(args) != 1 ): raise Exception('One argument alone expected to reverse function')
       if ( isinstance( args[0], str ) or isinstance( args[0], unicode) ):
           return String(args[0][::-1]) #string-reverse
       
       return list.reverse(args[0])
    
    @staticmethod
    def ezhil_pause(*args):
        if ( len(args) >= 1 ):
             print(args[0])
        if ( len(args) < 2 ):
             ezhil_sleep( 5 )
        else:
             ezhil_sleep( args[1] )
        return
    
    def add_builtin(self,call_name,call_handle,nargin=1,ta_alias=None):        
        # make sure you don't clobber yourself
        assert not self.builtin_map.get(call_name,None)
        if ( nargin == -1 ):
            self.builtin_map[call_name] = BlindBuiltins( call_handle, call_name, self.debug)
        else:
            self.builtin_map[call_name] = BuiltinFunction( call_handle, call_name, nargin, self.debug )
        # update the alias if something was supplied
        if ( ta_alias ):
            assert not self.builtin_map.get(ta_alias,None) #noclobber
            self.builtin_map[ta_alias] = self.builtin_map[call_name]
        
        return True
    
    def install_builtins(self):
        """ populate with the builtin functions"""
        self.builtin_map[u'printf']=BlindBuiltins(Interpreter.PRINTF,u'printf',self.debug)
        self.builtin_map[u'sprintf']=BlindBuiltins(Interpreter.SPRINTF,u'sprintf',self.debug)
        
        self.builtin_map['abs']=BlindBuiltins(abs,'abs',self.debug)
        self.builtin_map['all']=BlindBuiltins(all,'all',self.debug)
        self.builtin_map['any']=BlindBuiltins(any,'any',self.debug)
        if not PYTHON3:
            self.builtin_map['apply']=BlindBuiltins(apply,'apply',self.debug)
            self.builtin_map['buffer']=BlindBuiltins(buffer,'buffer',self.debug)
            self.builtin_map['cmp']=BlindBuiltins(cmp,'cmp',self.debug)
        self.builtin_map['basestring']=BlindBuiltins(str,'basestring',self.debug)
        self.builtin_map['bin']=BlindBuiltins(bin,'bin',self.debug)
        self.builtin_map['bool']=BlindBuiltins(bool,'bool',self.debug)
        self.builtin_map['bytearray']=BlindBuiltins(bytearray,'bytearray',self.debug)
        self.builtin_map['bytes']=BlindBuiltins(bytes,'bytes',self.debug)
        self.builtin_map['callable']=BlindBuiltins(callable,'callable',self.debug)
        self.builtin_map['chr']=BlindBuiltins(chr,'chr',self.debug)
        #self.builtin_map['classmethod']=BlindBuiltins(classmethod,'classmethod',self.debug)
        #self.builtin_map['coerce']=BlindBuiltins(coerce,'coerce',self.debug)
        self.builtin_map['compile']=BlindBuiltins(compile,'compile',self.debug)
        self.builtin_map['complex']=BlindBuiltins(complex,'complex',self.debug)

        # special ezhil commands
        self.builtin_map['copyright']=BlindBuiltins(ezhil_copyright,'copyright',self.debug)
        self.builtin_map['version']=BlindBuiltins(ezhil_version,'version',self.debug) 
        self.builtin_map['credits']=BlindBuiltins(ezhil_credits,'credits',self.debug)
        
        # global interpreter
        self.builtin_map['dir']=BlindBuiltins(ezhil_list_functions,'dir',self.debug)

        self.builtin_map['delattr']=BlindBuiltins(delattr,'delattr',self.debug)
        self.builtin_map['dict']=BlindBuiltins(dict,'dict',self.debug)
        self.builtin_map['python_dir']=BlindBuiltins(dir,'python_dir',self.debug)
        self.builtin_map['divmod']=BlindBuiltins(divmod,'divmod',self.debug)
        self.builtin_map['enumerate']=BlindBuiltins(enumerate,'enumerate',self.debug)

        # skip these system functions
        #self.builtin_map['eval']=BlindBuiltins(eval,'eval',self.debug)
        #self.builtin_map['execfile']=BlindBuiltins(execfile,'execfile',self.debug)
        #self.builtin_map['exit']=BlindBuiltins(exit,'exit',self.debug)
        if not PYTHON3:
            self.builtin_map['file']=BlindBuiltins(file,'file',self.debug)
            self.builtin_map['intern']=BlindBuiltins(intern,'intern',self.debug)
        
        self.builtin_map['filter']=BlindBuiltins(filter,'filter',self.debug)
        self.builtin_map['float']=BlindBuiltins(float,'float',self.debug)
        self.builtin_map['format']=BlindBuiltins(format,'format',self.debug)
        self.builtin_map['frozenset']=BlindBuiltins(frozenset,'frozenset',self.debug)
        self.builtin_map['getattr']=BlindBuiltins(getattr,'getattr',self.debug)
        #self.builtin_map['globals']=BlindBuiltins(globals,'globals',self.debug)
        self.builtin_map['hasattr']=BlindBuiltins(hasattr,'hasattr',self.debug)
        self.builtin_map['hash']=BlindBuiltins(hash,'hash',self.debug)
        self.builtin_map['help']=BlindBuiltins(help,'help',self.debug)
        self.builtin_map['hex']=BlindBuiltins(hex,'hex',self.debug)
        self.builtin_map['id']=BlindBuiltins(id,'id',self.debug)        
        self.builtin_map['int']=BlindBuiltins(int,'int',self.debug)
        self.builtin_map['isinstance']=BlindBuiltins(isinstance,'isinstance',self.debug)
        self.builtin_map['issubclass']=BlindBuiltins(issubclass,'issubclass',self.debug)
        self.builtin_map['iter']=BlindBuiltins(iter,'iter',self.debug)
        self.builtin_map['len']=BlindBuiltins(len,'len',self.debug)
        self.builtin_map['license']=BlindBuiltins(ezhil_license,'license',self.debug)
        self.builtin_map['long']=BlindBuiltins(int,'long',self.debug)
        self.builtin_map['map']=BlindBuiltins(map,'map',self.debug)
        #self.builtin_map['max']=BlindBuiltins(max,'max',self.debug)
        
        try:
            self.builtin_map['memoryview']=BlindBuiltins(memoryview,'memoryview',self.debug)
        except NameError as ie:
            if(self.debug): 
                print(u"Name Error:",unicode(ie))
    
        #self.builtin_map['min']=BlindBuiltins(min,'min',self.debug)
        self.builtin_map['next']=BlindBuiltins(next,'next',self.debug)
        self.builtin_map['object']=BlindBuiltins(object,'object',self.debug)
        self.builtin_map['oct']=BlindBuiltins(oct,'oct',self.debug)
        #self.builtin_map['open']=BlindBuiltins(open,'open',self.debug)
        self.builtin_map['ord']=BlindBuiltins(ord,'ord',self.debug)
        #self.builtin_map['pow']=BlindBuiltins(pow,'pow',self.debug)
        self.builtin_map['property']=BlindBuiltins(property,'property',self.debug)
        self.builtin_map['quit']=BlindBuiltins(quit,'quit',self.debug)
        self.builtin_map['range']=BlindBuiltins(range,'range',self.debug)        
        if not PYTHON3:
            self.builtin_map['reduce']=BlindBuiltins(reduce,'reduce',self.debug)
            self.builtin_map['reload']=BlindBuiltins(reload,'reload',self.debug)
            self.builtin_map['unicode']=BlindBuiltins(str,'unicode',self.debug)
        
        self.builtin_map['repr']=BlindBuiltins(repr,'repr',self.debug)
        self.builtin_map['reversed']=BlindBuiltins(reversed,'reversed',self.debug)
        self.builtin_map['round']=BlindBuiltins(round,'round',self.debug)
        self.builtin_map['set']=BlindBuiltins(set,'set',self.debug)
        self.builtin_map['setattr']=BlindBuiltins(setattr,'setattr',self.debug)
        self.builtin_map['slice']=BlindBuiltins(slice,'slice',self.debug)
        self.builtin_map['sorted']=BlindBuiltins(sorted,'sorted',self.debug)
        self.builtin_map['staticmethod']=BlindBuiltins(staticmethod,'staticmethod',self.debug)
        self.builtin_map['sum']=BlindBuiltins(sum,'sum',self.debug)
        self.builtin_map['super']=BlindBuiltins(super,'super',self.debug)
        self.builtin_map['tuple']=BlindBuiltins(tuple,'tuple',self.debug)
        self.builtin_map['type']=BlindBuiltins(type,'type',self.debug)
        self.builtin_map['unichr']=BlindBuiltins(chr,'unichr',self.debug)
        self.builtin_map['vars']=BlindBuiltins(vars,'vars',self.debug)
        if not PYTHON3:
            self.builtin_map['xrange']=BlindBuiltins(xrange,'xrange',self.debug)
        self.builtin_map['zip']=BlindBuiltins(zip,'zip',self.debug)
        
        # common/generic functions
        self.builtin_map['__getitem__']=BlindBuiltins(ezhil_getitem,"__getitem__")
        self.builtin_map['__setitem__']=BuiltinFunction(ezhil_setitem,"__setitem__",3)
        
        #file-IO functions
        self.builtin_map["file_open"]=BlindBuiltins(Interpreter.file_open,"file_open")
        self.builtin_map["file_close"]=BuiltinFunction(Interpreter.file_close,"file_close")
        self.builtin_map["file_read"]=BuiltinFunction(Interpreter.file_read,"file_read")
        self.builtin_map["file_readlines"]=BuiltinFunction(Interpreter.file_readlines,"file_readlines")
        self.builtin_map["file_write"]=BuiltinFunction(Interpreter.file_write,"file_write",2)
        self.builtin_map["file_writelines"]=BuiltinFunction(Interpreter.file_writelines,"file_writelines",2)
        
        # input statements
        self.builtin_map["input"]=BuiltinFunction(Interpreter.INPUT,"input")
        self.builtin_map["raw_input"]=BuiltinFunction(Interpreter.RAWINPUT,"raw_input")

        # assert
        self.builtin_map["assert"]=BuiltinFunction(Interpreter.ezhil_assert,"assert")
    
        # sleep/pause
        self.builtin_map["sleep"]=BuiltinFunction(ezhil_sleep,"sleep")
        self.builtin_map["pause"]=BlindBuiltins(Interpreter.ezhil_pause,"pause")
    
        # date/time
        self.add_builtin("date_time",ezhil_date_time,nargin=0,ta_alias=u"தேதி_நேரம்")
        self.add_builtin("time",time.time,nargin=0,ta_alias=u"நேரம்")
        self.add_builtin("ctime",time.ctime,nargin=1,ta_alias=u"cநேரம்")
        self.add_builtin("clock",time.time,nargin=0)

        # islist, isnumber predicates
        self.add_builtin("islist",ezhil_islist,nargin=1,ta_alias=u"பட்டியலா")
        self.add_builtin("isnumber",ezhil_isnumber,nargin=1,ta_alias=u"எண்ணா")    
	
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
        #self.builtin_map["exit"]=BuiltinFunction(min,"exit",1)

        # turtle functions - optional - 
        try:
            # turtle graphics
            from EZTurtle import EZTurtle

            turtle_attrib = EZTurtle.functionAttributes();
            for nargs,fcnName in list(turtle_attrib.items()):
                for vv in fcnName:
                    turtlefcn = u"turtle_"+vv;
                    if ( self.debug ): print(nargs, vv)
                    if ( nargs == -1 ):
                        self.builtin_map[turtlefcn] = BlindBuiltins(getattr(EZTurtle, vv),vv,self.debug)
                    else:
                        self.builtin_map[turtlefcn] = BuiltinFunction( getattr( EZTurtle, vv ), turtlefcn, nargs )
        except ImportError as ie:
            if ( self.debug ): 
                print(u"Cannot Import EZTurtle module; ignoring for now")
        # all builtin functions should pass the following test:
        # for attr in dir(module):
        #     assert callable( getattr( module, attr ) )
        # non-callable attributes cannot be in the builtins list        
        # string module builtins
        self.builtin_map["find"] = BuiltinFunction(str.find,"find",2)
        if not PYTHON3:
            self.builtin_map["atof"] = BuiltinFunction(string.atof,"atof",1)
            self.builtin_map["atof_error"] = BuiltinFunction(string.atof_error,"atof_error",1)
            self.builtin_map["atoi"] = BuiltinFunction(string.atoi,"atoi",1)
            self.builtin_map["atoi_error"] = BuiltinFunction(string.atoi_error,"atoi_error",1)
            self.builtin_map["atol"] = BuiltinFunction(string.atol,"atol",1)
            self.builtin_map["atol_error"] = BuiltinFunction(string.atol_error,"atol_error",1)
            self.builtin_map["capitalize"] = BuiltinFunction(string.capitalize,"capitalize",1)
            self.builtin_map["capwords"] = BuiltinFunction(string.capwords,"capwords",1)
            self.builtin_map["center"] = BuiltinFunction(string.center,"center",1)
            self.builtin_map["count_string"] = BuiltinFunction(string.count,"count",1)
            self.builtin_map["expandtabs"] = BuiltinFunction(string.expandtabs,"expandtabs",1)

        self.builtin_map["index_string"] = BuiltinFunction(str.index,"index",2)
        if not PYTHON3:
            self.builtin_map["index_error"] = BuiltinFunction(string.index_error,"index_error",1)
        self.builtin_map["join"] = BuiltinFunction(str.join,"join",1)
        if not PYTHON3:
            self.builtin_map["joinfields"] = BuiltinFunction(string.joinfields,"joinfields",1)
        self.builtin_map["ljust"] = BuiltinFunction(str.ljust,"ljust",1)
        self.builtin_map["lower"] = BuiltinFunction(str.lower,"lower",1)
        self.builtin_map["lstrip"] = BuiltinFunction(str.lstrip,"lstrip",1)
        self.builtin_map["maketrans"] = BuiltinFunction(string.maketrans,"maketrans",1)
        self.builtin_map["replace"] = BuiltinFunction(str.replace,"replace",3)
        self.builtin_map["rfind"] = BuiltinFunction(str.rfind,"rfind",2)
        self.builtin_map["rindex"] = BuiltinFunction(str.rindex,"rindex",1)
        self.builtin_map["rjust"] = BuiltinFunction(str.rjust,"rjust",1)
        self.builtin_map["rsplit"] = BuiltinFunction(str.rsplit,"rsplit",1)
        self.builtin_map["rstrip"] = BuiltinFunction(str.rstrip,"rstrip",1)
        self.builtin_map["split"] = BuiltinFunction(str.split,"split",2)
        if not PYTHON3:
            self.builtin_map["splitfields"] = BuiltinFunction(string.splitfields,"splitfields",1)
        self.builtin_map["strip"] = BuiltinFunction(str.strip,"strip",1)
        self.builtin_map["swapcase"] = BuiltinFunction(str.swapcase,"swapcase",1)
        self.builtin_map["translate"] = BuiltinFunction(str.translate,"translate",1)
        self.builtin_map["upper"] = BuiltinFunction(str.upper,"upper",1)
        self.builtin_map["zfill"] = BuiltinFunction(str.zfill,"zfill",2)
        # get/set methods are handled by generic __getitem__ and __setitem__
        
        # list methods - first argument, when required, is always a list obj
        self.builtin_map["append"] = BuiltinFunction(list.append,"append",2)
        self.builtin_map["insert"] = BuiltinFunction(list.insert,"insert",3)
        self.builtin_map["index"] = BuiltinFunction(list.index,"index",2)
        self.builtin_map["list"] = BuiltinFunction(list,"list",0)        
        self.builtin_map["sort"] = BuiltinFunction(list.sort,"sort",1)
        self.builtin_map["count"]= BuiltinFunction(list.count,"count",2)
        self.builtin_map["extend"]= BuiltinFunction(list.extend,"extend",2)
        self.builtin_map["reverse"]= BuiltinFunction(Interpreter.ezhil_reverse,"reverse",1)
        self.builtin_map["pop_list"] = BuiltinFunction(list.pop,"pop",1)

        # dictionary methods - first argument, when required, is always a dict obj
        self.builtin_map["clear"]= BuiltinFunction(dict.clear,"clear",1)
        self.builtin_map["copy"]= BuiltinFunction(dict.copy,"copy",1)
        self.builtin_map["fromkeys"]= BuiltinFunction(dict.fromkeys,"fromkeys",1)
        self.builtin_map["items"]= BuiltinFunction(dict.items,"items",1)
        
        if not PYTHON3:
            self.builtin_map["has_key"]= BuiltinFunction(dict.has_key,"has_key",1)
            self.builtin_map["iteritems"]= BuiltinFunction(dict.iteritems,"iteritems",1)
            self.builtin_map["iterkeys"]= BuiltinFunction(dict.iterkeys,"iterkeys",1)
            self.builtin_map["itervalues"]= BuiltinFunction(dict.itervalues,"itervalues",1)
            self.builtin_map["pop_dict"]= BuiltinFunction(dict.pop,"pop",1)
            self.builtin_map["popitem"]= BuiltinFunction(dict.popitem,"popitem",1)
            self.builtin_map["setdefault"]= BuiltinFunction(dict.setdefault,"setdefault",1)
        
        self.builtin_map["keys"]= BuiltinFunction(dict.keys,"keys",1)
        self.builtin_map["update"]= BuiltinFunction(dict.update,"update",1)
        self.builtin_map["values"]= BuiltinFunction(dict.values,"values",1)
	
        # open-tamil API
        # get tamil letters
        self.add_builtin("get_tamil_letters",tamil.get_letters,nargin=1,ta_alias=u"தமிழ்_எழுத்துக்கள்")
        self.add_builtin(u"த",tamil.get_letters,nargin=1)
        self.add_builtin("tamil_length",ezhil_tamil_length,nargin=1,ta_alias=u"தநீளம்")     
        
        # functions returning constant list of Tamil strings
        self.add_builtin("tamil_letters",lambda :  tamil.tamil_letters,
                         nargin=0,ta_alias=u"தமிழ்எழுத்து")
        self.add_builtin("tamil_uyir",lambda :  tamil.uyir_letters,
                         nargin=0,ta_alias=u"உயிர்எழுத்து")
        self.add_builtin("tamil_mei",lambda: tamil.mei_letters,
                         nargin=0,ta_alias=u"மெய்எழுத்து") 
        self.add_builtin("tamil_kuril",lambda: tamil.kuril_letters,
                         nargin=0,ta_alias=u"குரில்எழுத்து") 
        self.add_builtin("tamil_nedil",lambda: tamil.nedil_letters,
                         nargin=0,ta_alias=u"நேடில்எழுத்து") 
        self.add_builtin("tamil_vallinam",lambda: tamil.vallinam_letters,
                         nargin=0,ta_alias=u"வல்லினம்எழுத்து") 
        self.add_builtin("tamil_mellinam",lambda: tamil.mellinam_letters,
                         nargin=0,ta_alias=u"மெல்லினம்") 
        self.add_builtin("tamil_idayinam",lambda: tamil.idayinam_letters,
                         nargin=0,ta_alias=u"இடைனம்எழுத்து") 
        self.add_builtin("tamil_agaram",lambda: tamil.agaram_letters,
                         nargin=0,ta_alias=u"அகரம்எழுத்து") 
        self.add_builtin("tamil_uyirmei",lambda: tamil.uyirmei_letters,
                         nargin=0,ta_alias=u"உயிர்மெய்எழுத்து")
        
        self.add_builtin("tamil_istamil_prefix",tamil.istamil_prefix,
                         nargin=1)
        ##NEEDS FIX
        ##self.add_builtin("tamil_all_tamil", tamil.all_tamil,
                    ##      nargin=1,ta_alias=u"தனித்தமிழா")
        self.add_builtin("tamil_hastamil",tamil.has_tamil,
                         nargin=1,ta_alias=u"தமிழ்கொண்டதா")
        self.add_builtin("tamil_reverse_word",tamil.reverse_word,
                         nargin=1,ta_alias=u"அந்தாதிமாற்று")
        return True
    
    def __repr__(self):
        rval =  u"[Interpreter: "
        rval = rval + u"[Functions["
        for k in list(self.function_map.keys()):
            rval = rval + u"\n "+ unicode(self.function_map[k]) 
        rval = rval +u"]] "+ unicode(self.ast) +u"]\n"
        return rval

    def parse(self):
        """ parser routine """
        self.ast = self.parser.parse()
        return self.ast

    def evaluate(self):
        env = Environment( self.call_stack, self.function_map, \
                               self.builtin_map, self.debug, int(self.MAX_REC_DEPTH/10) )
        env.call_function("__toplevel__") ##some context
        return self.ast.evaluate(env)

    def evaluate_interactive(self,env = None):
        ## use a persistent environment for interactive interpreter
        if ( not env ):
            if ( self.debug ): 
                print("creating a new environment")
            
            env = Environment( self.call_stack, self.function_map, \
                                   self.builtin_map, self.debug )
            env.call_function("__toplevel__") ##some context
        ## use this from the interactive-interpreter
        rval = self.ast.evaluate(env)
        return [ rval, env ]

# world-famous REPL
# derive from the Python standard library - Cmd
# refactor out REPL for ezhil and exprs
class REPL(Cmd):
    def __init__(self,lang, lexer, parse_eval, debug=False):
        """ @lexer is language lexical analyzer
            @parse_eval is the language interpreter with builtins, runtime, parser etc..
            @lang is a descriptive string,
            @debug the boolean """
        Cmd.__init__(self)
        ## ala-Python like
        self.banner = u"""எழில் - ஒரு தமிழ் நிரலாக்க மொழி (Sat Mar 14 17:53:58 EDT 2015)
Ezhil : A Tamil Programming Language - version %g, (C) 2007-2015
Type "help", "copyright", "credits" or "license" for more information."""%ezhil_version()
        
        self.lang = lang
        self.lexer = lexer
        self.parse_eval = parse_eval
        self.debug = debug
        self.line_no = 1
        self.env = None ## get the first instance from evaluate_interactive
        self.prevlines = u'' ## support for continued lines
        self.cmdloop()
    
    def parseline(self,line):
        arg,cmd = u"",u""
        line = line.decode("utf-8")
        if line in [u"exit",u"help",u"EOF",u"copyright",u"credits",u"license"]:
            cmd = line
            line = line+u"()"
        return [cmd,arg,line]

    def update_prompt(self):
        self.prompt = u"%s %d>> "%(self.lang,self.line_no)

    def continuedline(self):
        return len(self.prevlines) > 0
        
    def preloop(self):
        if not self.continuedline():
            self.update_prompt()
        print(self.banner)
    
    def emptyline(self):
        pass
    
    def default(self,line):
        """ REPL is carried out primarily through this callback from the looping construct """
        self.line_no += 1
        line = unicode(line)
        if ( self.debug ): print("evaluating line", line)
        if ( line == 'exit' ): self.exit_hook(doExit=True)
        try:
            self.lexer.set_line_col([self.line_no, 0])
            if len(self.prevlines) > 0:
                total_line = self.prevlines + u'\n' + line
            else:
                total_line = line
            self.lexer.tokenize(total_line)
            #self.lexer.warn_incomplete_tokens()
            nbraces = list()
            COMPLEMENT = {'}':'{',')':'(',']':'['}
            for TKN_idx in range(len(self.lexer.tokens)-1,-1,-1):
                TKN = self.lexer.tokens[ TKN_idx ]
                if ( self.debug ): print(TKN, TKN_idx)
                if TKN.val in ["(", "[", "{"]:
                    nbraces.append(TKN.val)
                elif TKN.val in [")","]","}"]:
                    if len(nbraces) > 0 and nbraces[-1] == COMPLEMENT[TKN.val]:
                        del nbraces[-1]
                        if ( self.debug ): print("matched braces..")
                else:
                    if ( self.debug ): print("nota brace token",TKN.val)
            if len(nbraces) > 0:
                if ( self.debug ): 
                    print ("MIsmatched braces")
                    for idx in nbraces:
                        print(idx)
                self.prevlines += u'\n' + line
                self.lexer.reset() #reset lexer
                return
            else:
                if ( self.debug ): print ("Braces matched")
                self.prevlines = u''
            [line_no,c] = self.lexer.get_line_col( 0 )
            if ( self.debug ): self.lexer.dump_tokens()
            
            self.prevlines = u'' #erase prev
            self.parse_eval.parse()
            if ( self.debug ):
                print(u"*"*60);  
            [rval, self.env] = self.parse_eval.evaluate_interactive(self.env)
            if ( self.debug ): print( u"return value", unicode(rval) )
            if hasattr( rval, 'evaluate' ):
                pprint(rval.__str__())
            elif hasattr(rval,'__str__'): #print everything except a None object
                pprint( rval )
        except Exception as excep:
            print(u"Exception in code, at line %d,  \"%s\" \n >>>>>>> %s "%(self.line_no-1,line,unicode(excep)))
            if ( self.debug ):
                raise excep
                ## clear tokens in lexer
        if ( self.debug ): print(self.env)
        self.lexer.tokens = list()
        self.update_prompt()
    
    def do_EOF(self,line):
        print(u"\n")
        self.exit_hook()
        return True
    
    def exit_hook(self,doExit=False):
        if ( self.lang == u"எழில்"):
            print(u"******* வணக்கம்! பின்னர் உங்களை  பார்க்கலாம். *******") 
        else:
            print(u"******* Goodbye! Now have a nice day *******")
        if doExit:
            sys.exit( 0 )
        return

# program name / CLI args handler
def get_prog_name(lang):
    prog_name=None
    debug=False
    parser = argparse.ArgumentParser(prog=lang)
    parser.add_argument("files",nargs='*',default=[])
    parser.add_argument("-debug",action="store_true",
                        default=False,
                        help="enable debugging information on screen")
    parser.add_argument("-tamilencoding",default="UTF-8",
                        help="option to specify other file encodings; supported  encodings are TSCII, and UTF-8")
    parser.add_argument("-stdin",action="store_true",
                        default=None,
                        help="read input from the standard input")
    args = parser.parse_args()
    if args.debug:
        print("===>",args.tamilencoding," | ===> files: ".join(args.files))
    error_fcn = lambda :   parser.print_help() or sys.exit(-1)
    if (len(args.files) == 0 and (not args.stdin)):
        error_fcn()
    if not(args.tamilencoding in ["utf-8","tscii","TSCII","UTF-8"]):
        print("Unsupported encoding %s; use values TSCII or UTF-8, or see Help"%args.tamilencoding)
        error_fcn()
    prog_name = args.files
    debug = args.debug
    dostdin = args.stdin
    encoding = args.tamilencoding
    if args.debug:
        print("###### chosen encoding => ",encoding)
    return [prog_name, debug, dostdin,encoding]
