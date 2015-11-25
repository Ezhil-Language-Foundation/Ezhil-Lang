#!/usr/bin/python
# -*- coding: utf-8 -*-
## 
## (C) 2015 Muthiah Annamalai
## Licensed under GPL Version 3
## 
## Interpreter for Ezhil language
from __future__ import print_function

## Tx
from transform import Visitor, TransformVisitor
## AST elements
from ast import Expr, ExprCall, ExprList, Stmt, ReturnStmt, \
 BreakStmt, ContinueStmt, ElseStmt, IfStmt, WhileStmt, \
 ForStmt, AssignStmt, PrintStmt, EvalStmt, ArgList, \
 ValueList, Function, StmtList, Identifier, Number, \
 String, Boolean

from errors import RuntimeException

class TransformEntryExitProfile(TransformVisitor):
    def __init__(self,**kwargs):
        TransformVisitor.__init__(self,**kwargs)
        
    def visit_program_or_script(self,stmt_list):
        l,c=0,0
        stmt_list.dbg_msg(" add call : profile(\"begin\")")
        begin = ValueList([String("begin")],l,c,self.debug)
        call_profile_begin = ExprCall( Identifier("profile",l,c), begin, l, c, self.debug )
        stmt_list.List.insert(0,call_profile_begin)
        
        stmt_list.dbg_msg(" add call : 'profile(\"results\")'")
        results = ValueList([String("results")],l,c,self.debug)
        call_profile_results = ExprCall( Identifier("profile",l,c), results, l, c, self.debug )
        stmt_list.append( call_profile_results )
        return

class TransformSafeModeFunctionCheck(TransformVisitor):
    def __init__(self,**kwargs):
        self.forbidden_fcn_names = [u'raw_input',u'input',u'fopen',u'open',u'fclose',\
        u'உள்ளீடு',u'turtle',u'கோப்பை_எழுது',u'கோப்பை_திற',u'கோப்பை_மூடு']
        TransformVisitor.__init__(self,**kwargs)
        
    def visit_expr_call(self,expr_call):
        callee = expr_call.func_id.id
        if callee in self.forbidden_fcn_names:
           raise RuntimeException(u"ERROR %s:\n\t %s may not be used in SAFE MODE ."%(self.interpreter.get_fname(),unicode(expr_call)))
        expr_call.arglist.visit( self )
        return
