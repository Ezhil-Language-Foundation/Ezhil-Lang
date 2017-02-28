#!/usr/bin/python
## -*- coding: utf-8 -*-
## (C) 2007, 2008, 2013-2015 Muthiah Annamalai
## Licensed under GPL Version 3
##
## This module is the runtime elements for the exprs language.
## It contains classes 
## 

from .errors import RuntimeException
import keyword
import sys
import time
import traceback
from .profile import Profiler

PYTHON3 = (sys.version[0] == '3')
if PYTHON3:
    unicode = str

# customize I/O like functions for external GUI
class EzhilCustomFunction(object):
    _instance = None
    def __init__(self):
        object.__init__(self)
        if PYTHON3:
            self.raw_input_fcn = input 
        else:
            self.raw_input_fcn = raw_input 
    @staticmethod
    def get_instance():
        if not EzhilCustomFunction._instance:
            EzhilCustomFunction._instance = EzhilCustomFunction()
        return EzhilCustomFunction._instance
    
    @staticmethod
    def raw_input(args):
        return EzhilCustomFunction.get_instance().raw_input_fcn(args)
    
    @staticmethod
    def reset():
        if PYTHON3:
            EzhilCustomFunction.get_instance().raw_input_fcn = input
        else:
            EzhilCustomFunction.get_instance().raw_input_fcn = raw_input
    
    @staticmethod
    def set(newfcn):
        EzhilCustomFunction.get_instance().raw_input_fcn = newfcn
    
## RUNTIME / LIBRARY etc
class DebugUtils:
    def __init__(self,dbg):
        self.debug = dbg

    def dbg_msg(self, msg):
        """ handy to print debug messages """
        if ( self.debug ):
            print(u"## ",msg)
        return

class BuiltinFunction:
    """ a templatized way to invoke bulitin functions."""
    def __init__(self,fn,name,padic=1,dbg = False):
        self.fn = fn
        self.name = name
        self.use_adicity = True
        self.padic = padic
        self.debug = dbg
        self.aslist = False
        
    def __str__(self):
        return u"[BuiltinFunction[%s,nargs=%d]]"%(self.name,self.padic)
    
    def evaluate(self,env):
        try:
            return self.do_evaluate(env)
        except AssertionError as assert_excep:
            env.unroll_stack()
            raise RuntimeException( unicode(assert_excep) + u' Assertion failed!')
        except Exception as excep:
            env.unroll_stack()            
            print(u"failed dispatching function ",unicode(self),u"with exception",unicode(excep))
            if ( self.debug ):
                traceback.print_tb(sys.exc_info()[2])
            raise excep
        
    def do_evaluate(self,env):
        ## push stuff into the call-stack
        env.call_function(self.name)
        
        ## check arguments match, otherwise raise error
        args = env.get_args()#.get_list()
        env.set_local({})

        if ( self.use_adicity and len(args) < self.padic ):
            raise RuntimeException("Too few args to bulitin function " + self.name)

        # keep evaluating for as many evaluate object-methods are available
        # because Python libraries don't recognize ezhil AST objects.
        while( any(filter(lambda x: hasattr(x,'evaluate'),args)) ):            
            args_ = []
            for a in args:
                if hasattr(a,'evaluate'):
                    a = a.evaluate(env)
                args_.append(a)
            args = args_
        
        if ( self.use_adicity ):
            if ( self.debug ): print(self.fn, args, self.padic)
            rval = self.fn(*args)
        else:
            try:                
                if ( self.aslist ):
                    rval = self.fn(*[args])
                else:
                    rval = self.fn(*args)
            except AssertionError as assert_excep:
                raise assert_excep
            except Exception as excep:
                #print u"catch exception", excep
                raise RuntimeException( unicode(excep) )
        env.clear_call(copyvars= self.name in ["execute","eval",u'இயக்கு',u'மதிப்பீடு'])
        ## pop stuff into the call-stack
        env.return_function(self.name)
        return  rval

class BlindBuiltins(BuiltinFunction):
    """ also blindly include all functions from the 
        os, sys, curses.ascii, math etc. donot check arguments 
        here.    """
    def __init__(self,fn,name,dbg = False,aslist=False,padic=-1):
        BuiltinFunction.__init__(self,fn,name,padic,dbg)
        self.use_adicity = False
        self.aslist = aslist
        
    def __unicode__(self):
        return BuiltinFunction.__str__(self)

class CountDownTimer(object):
    def __init__(self):
        object.__init__(self)
        self._engaged = False
        self._safeModeTimeout = 13  # seconds of wall clock timeout for Ezhil codes in SAFE MODE
        self._startTime = 0

    # all times are wall clock times
    def is_timeout(self):
        if not self._engaged:
            return False
        now = time.time()
        rval = (now - self._startTime) > self._safeModeTimeout
        if rval:
            self._engaged = False
        return rval

    def record_start_time(self):
        self._startTime = time.time()
        self._engaged = True
        return

    # update safe mode timeout
    def set_timeout(self, seconds):
        assert seconds > 0
        self._safeModeTimeout = seconds


# <<Side-Effects>>: computation is side-effect of programming.
class Environment(CountDownTimer):
    """ used to manage the side-effects of an interpreter """
    def __init__(self, call_stack, function_map, builtin_map, dbg = False, MAX_REC_DEPTH  = 128 ):
        CountDownTimer.__init__(self)
        self.do_profiling = False
        self.profiler = None
        self.max_recursion_depth = MAX_REC_DEPTH #keep it smaller than Python stack
        self.call_stack = call_stack#list
        self.function_map = function_map#dicts
        self.builtin_map = builtin_map#dicts
        self.local_vars = []#list of dicts.
        self.arg_stack = []#list of lists
        self.ret_stack = [] #list
        self.debug = dbg #use to turn debugging on.
        self.readonly_global_vars = {'True':True, 'False':False,u"மெய்":True, u"பொய்":False} #dict of global vars
        self.clear_break_return_continue()

    def validate_timer(self):
        # time to be reset everytime the interpreter calls evaluate
        if self.is_timeout():
            raise RuntimeException("Evaluation of your program is taking too long!\n"
                                   "\tTimeout exceeded %g (seconds)"%self._safeModeTimeout)
        return

    def __del__(self):
        if (self.debug): print(u"deleting environment")
        
    def enable_profiling(self):
        self.validate_timer()
        self.do_profiling =True
        self.profiler = Profiler()
        return
    
    def is_profiling(self):
        self.validate_timer()
        return self.do_profiling
    
    def disable_profiling(self):
        self.validate_timer()
        self.do_profiling = False
        
    def report_profiling(self):
        self.validate_timer()
        self.disable_profiling()
        self.profiler.report_stats()
        
    def reset_profiling(self):
        self.validate_timer()
        self.disable_profiling()
        self.profiler = None
        
    def unroll_stack(self):
        self.validate_timer()
        # we skip BOS since it is a __toplevel__
        if (self.debug): print("clearing locals")
        if len(self.call_stack) > 0:
            if self.call_stack[-1][0] != "__toplevel__":
                self.clear_call()
        
        for i in range(1,len(self.call_stack)):
            print(u"%sError in function '%s'%s:"%(u" "*(i-1),self.call_stack[i][0],self.call_stack[i][1]))
        while len(self.call_stack) > 0:
            tos,_ = self.call_stack.pop()
            #print(u"Error in location %s"%str(tos))
        return
    
    def get_break_return(self):
        self.validate_timer()
        """ get if break or return was set for use in loops """
        val = self.Break or self.Return
        return val

    def clear_break(self):
        self.validate_timer()
        """ reset after a break statement """
        self.Break = False
        return False

    def clear_continue(self):
        self.validate_timer()
        """ reset after a continue statement """
        self.Continue = False
        return False

    def set_break(self):
        self.validate_timer()
        """ execute a continue statement """
        self.Break = True
        return True

    def set_continue(self):
        self.validate_timer()
        """ execute a continue statement """
        self.Continue = True
        return True
    
    def break_return_continue(self):
        self.validate_timer()
        val = ( self.Break or 
                 self.Return or 
                 self.Continue )
        ## must clear continue flag right away.
        if ( self.Continue ):
            self.Continue = False
        return val
    
    def dbg_msg(self, msg):
        """ handy to print debug messages """
        if ( self.debug ):
            print(msg)
        return
    
    def __unicode__(self):
        if (self.debug):
            return repr(self)
        return u"<env>"
    
    def __repr__(self):
        retval = u"CallStack =>"+unicode(self.call_stack) + u"\n" \
            u"LocalVars =>"+ unicode(self.local_vars) + u"\n" \
            u"ArgStack =>"+ unicode(self.arg_stack) + u"\n" 
        return retval

    def set_retval( self, rval ):
        self.validate_timer()
        self.ret_stack.append( rval )
        self.Return = True
        return
    
    def get_retval( self ):
        self.validate_timer()
        rval = None
        if ( len(self.ret_stack ) >= 1  ):
            rval = self.ret_stack.pop()
        return rval

    def clear_break_return_continue(self):
        self.validate_timer()
        self.Break = False
        self.Return = False
        self.Continue = False

    def clear_call(self,copyvars=False):
        self.validate_timer()
        """ utility to cleanup the stacks etc.. """
        self.clear_local( copyvars ) 
        self.clear_args ( )
        self.clear_break_return_continue()
        
    def clear_args(self):
        self.validate_timer()
        """ cleanup the stack """
        self.arg_stack.pop()
        return

    def get_args(self):
        self.validate_timer()
        """ manage a global argument stack """
        return self.arg_stack[-1]

    def set_args(self,val):
        self.validate_timer()
        """ manage a global argument stack """
        self.dbg_msg( "setting args " + unicode( val ) )
        return self.arg_stack.append(val)
    
    def set_local(self, vars):
        self.validate_timer()
        self.local_vars.append(vars)
        self.dbg_msg( "setting locals " + unicode( vars ) )
        self.clear_break_return_continue()
        return
    
    def clear_local(self,copyvars=False):
        self.validate_timer()
        prev_values = self.local_vars.pop()
        if copyvars:
            if len(self.local_vars) < 1:
                self.local_vars.append({})
            self.local_vars[-1].update(prev_values)
        return
    
    def has_id(self, idee):
        """ check various 'scopes' for ID variable """
        self.validate_timer()
        rval = False
        if idee in self.readonly_global_vars:
            return True
        if ( len( self.local_vars ) == 0 ):
            return False
        variables = self.local_vars[-1]
        rval = idee in variables
        return rval

    def set_id(self, idee, val, global_id = False):
        """ someday do global_id """
        self.validate_timer()
        if idee in self.readonly_global_vars:
            raise Exception(u"Error: Attempt to reassign constant %s"%idee)
        if ( len(self.local_vars) > 0 ):
            d=self.local_vars[-1]
        else:
            d=dict()
            self.local_vars.append(d)
        #if not (idee in d) and (idee in self.global_vars):
        #    self.global_vars[idee] = val
        # else:
        d[idee]=val
        self.dbg_msg("set_id: " + unicode(idee) +" = "+unicode(val))
        return

    def get_id(self, idee):
        self.validate_timer()
        val = None
        if idee in self.readonly_global_vars:
            return self.readonly_global_vars[idee]
        if not self.has_id(idee):
            note = ''
            if idee in keyword.kwlist:
                note = 'Did you possibly confuse the Python english keyword %s for Ezhil keyword ?'%idee
            raise RuntimeException("Identifier %s not found"%idee)
        variables = self.local_vars[-1]
        val = variables[idee]
        self.dbg_msg("get_id: val = "+unicode(val))
        return val

    def call_function(self, fn,callsite=u""):
        """ set call stack, used in function calls. Also check overflow"""
        self.validate_timer()
        if ( len(self.call_stack) >= self.max_recursion_depth ):
            raise RuntimeException( "Maximum recursion depth [ " + 
                                    unicode(self.max_recursion_depth) + 
                                    " ] exceeded; stack overflow." )
        self.dbg_msg(u"calling function"+unicode(fn)+callsite)
        if ( self.is_profiling() ):
            self.profiler.add_function( fn )
        self.call_stack.append( (fn,callsite) ) 
    
    def return_function(self, fn):
        self.validate_timer()
        va,_ = self.call_stack.pop( )
        if ( fn != va ):
            raise RuntimeException("function %s doesnt match Top-of-Stack"%fn)
        if ( self.is_profiling() ):
            self.profiler.update_function( va )
        return va
    
    def has_function(self, fn):
        self.validate_timer()
        if ( fn in self.builtin_map ):
            return True
        if ( fn in self.function_map ):
            return True
        return False
    
    def get_function(self, fn):
        self.validate_timer()
        if not self.has_function(fn):
            raise RuntimeException("undefined function: "+fn)

        if ( fn in self.builtin_map ):
            return self.builtin_map[fn]
        
        if ( fn in self.function_map ):
            return self.function_map[fn] 
        
        raise RuntimeException("Environment error on fetching function "+fn)
