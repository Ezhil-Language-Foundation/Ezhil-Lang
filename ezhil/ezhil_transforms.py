#!/usr/bin/python
# -*- coding: utf-8 -*-
## 
## (C) 2015 Muthiah Annamalai
## Licensed under GPL Version 3
## 
## Interpreter for Ezhil language
from __future__ import print_function

import sys
PYTHON3 = (sys.version[0] == '3')
if PYTHON3:
    unicode = str

## Tx
from transform import Visitor, TransformVisitor
from scanner import Token
## AST elements
from ast import Expr, ExprCall, ExprList, Stmt, ReturnStmt, \
 BreakStmt, ContinueStmt, ElseStmt, IfStmt, WhileStmt, \
 ForStmt, AssignStmt, PrintStmt, EvalStmt, ArgList, \
 ValueList, Function, StmtList, Identifier, Number, \
 String, Boolean

from errors import RuntimeException, SemanticException

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

#  Type checker for ezhil - rules list #65
class TransformSemanticAnalyzer(TransformVisitor):
    def __init__(self,**kwargs):
        TransformVisitor.__init__(self,**kwargs)
        return
    
# Find a list of rules for type checking Ezhil AST.
# You may only add like types. I.e. (You may only add numbers or strings but never between each other)
# You may index arrays with only integers or numbers or dictionaries with Strings
# You can type check argument types, and number of builtin functions.
# You may type check arguments for number of args in a function call.
    
    def visit_expr_call(self,expr_call):
        callee = expr_call.func_id.id
        if callee == u"__getitem__":
            # T.B.D
            pass
        expr_call.arglist.visit( self )
        return
    
    # check if the constants are on lhs of assignment statements
    # check if the strings are added to numbers 
    # check ...
    def visit_assign_stmt(self, assign_stmt):
        if any( map( lambda typename: isinstance( assign_stmt.lvalue, typename) , [Number,String,Boolean,Function]) ):
            raise SemanticException("Cannot use number, string, constant or functions on LHS of assignment %s"%unicode(assign_stmt))
        assign_stmt.lvalue.visit( self )
        assign_stmt.rvalue.visit( self )
        return
    
    def visit_binary_expr(self,binexpr):
        lhs_is_string = isinstance( binexpr.term, String)
        rhs_is_string = isinstance( binexpr.next_expr, String )
        lhs_id_expr_call = isinstance( binexpr.term, ExprCall ) or isinstance( binexpr.term, Identifier)
        rhs_id_expr_call = isinstance( binexpr.next_expr, ExprCall ) or isinstance( binexpr.next_expr, Identifier)
        
        if isinstance(binexpr.next_expr,Expr):
            binexpr.next_expr.visit(self)
            return
        
        binexpr.term.visit(self)
        
        if binexpr.binop.kind != Token.PLUS:
            if lhs_is_string or rhs_is_string:
                if binexpr.binop.kind in Token.COMPARE:
                    pass
                else:
                    raise SemanticException("Cannot use string with operators other than '+','>=','<=','!=','==','>','<' at expression %s"%unicode(binexpr))
        else:
            if lhs_is_string or rhs_is_string:
                if not ((lhs_is_string and rhs_is_string) or \
                   (lhs_is_string and rhs_id_expr_call) or \
                   (rhs_is_string and lhs_id_expr_call)):
                   raise SemanticException("Cannot join strings and expression at expression %s"%unicode(binexpr))
        return
    
    def visit_import(self,importstmt):
        if not isinstance(importstmt.filename,String):
            raise SemanticException("Import statement should be a string at time of interpretation at %s"%unicode(importstmt))
        return

class TransformConstantFolder(TransformVisitor):
    def __init__(self,**kwargs):
        TransformVisitor.__init__(self,**kwargs)
        return
        
    def can_fold_expr(self,expr):
        if isinstance(expr,Number):
            return True, expr
        
    def visit_binary_expr(self,binexpr):
        # if lhs is constant and you are able to fold rhs
        # then replace binexpr with the value
        
        if isinstance(binexpr.next_expr,Expr):
            binexpr.next_expr.visit(self)
            return
        
        binexpr.term.visit(self)
        
        lhs_is_num = isinstance( binexpr.term, Number)
        [foldable,val] = self.can_fold_expr( binexpr.next_expr )
        if foldable:
            # new API needed to replace the node
            self.binexpr.replace( self.constant_fold( binexpr ) )
        