#!/usr/bin/python
## -*- coding: utf-8 -*-
## 
## (C) 2008, 2013 Muthiah Annamalai
## Licensed under GPL Version 3
## 
## This module contains AST visitor for the Ezhil language.
## It is used by profiling insertion, semantic checks among
## others

from .ezhil_scanner import EzhilLex, EzhilToken
#from .Interpreter EzhilInterpreter

## Visitor template
class Visitor:
    def __init__(self):
        """ initialize data structures"""
        # self.codegen, pretty-printer, 
        # tree-source-transformer etc.

    def default(self,*args):
        raise Exception(u'Transform Visitor Not Implemented for AST [%s]'%str(args[0]))
    
    def visit_identifier(self, id):  
        self.default(id)
        return
    
    def visit_string(self, str):
        self.default(str)
        return

    def visit_number(self, num):
        self.default(num)
        return

    def visit_expr_call(self,expr_call):
        self.default(expr_call)
        return

    def visit_expr_list(self, expr_list):
        self.default(expr_list)
        return

    def visit_stmt( self, stmt):
        self.default(stmt)
        return

    def visit_expr(self, expr):
        self.default(expr)
        return

    def visit_return_stmt(self, ret_stmt):
        self.default(ret_stmt)
        return

    def visit_break_stmt(self, break_stmt ):
        self.default(break_stmt)
        return
    
    def visit_continue_stmt(self, cont_stmt):
        self.default(cont_stmt)
        return

    def visit_else_stmt(self,else_stmt):
        self.default(else_stmt)
        return

    def visit_if_elseif_stmt(self,if_elseif_stmt):
        self.default(if_elseif_stmt)
        return

    def visit_while_stmt(self,stmt):
        self.default(stmt)
        return

    def visit_for_stmt(self,for_stmt):
        self.default(for_stmt)
        return

    def visit_assign_stmt(self, assign_stmt):
        self.default(assign_stmt)
        return

    def visit_print_stmt(self, print_stmt):
        self.default(print_stmt)
        return

    def visit_eval_stmt(self, eval_stmt ):
        self.default(eval_stmt)
        return

    def visit_arg_list(self, arg_list):
        self.default(arg_list)
        return

    def visit_value_list(self,value_list):
        self.default(value_list)
        return

    def visit_stmt_list(self,stmt_list):
        self.default(stmt_list)
        return

    def visit_function(self,function):
        self.default(function)
        return
    
    def visit_program_or_script(self,parse_tree):
        # bootstrap if leaf class didn't override this one
        self.visit_stmt_list(parse_tree)
        return
        
    def visit_dict(self,dictobj):
        return
    
    def visit_array(self,arrayobj):
        return
        
    def visit_unaryexpr(self,unaryexp):
        unaryexp.term.visit(self)
        return
    
    def visit_binary_expr(self,binexpr):
        self.visit_expr(binexpr)
        return
    
    def visit_import(self,importstmt):
        return
    
class MockInterpreter(object):
    def __init__(self,parsetree):
        object.__init__(self)
        self.ast = parsetree
        self.lexer = None

def make_mock_interpreter(parsetree):
    mockObj = MockInterpreter(parsetree)
    return mockObj

class TransformVisitor(Visitor):
    def __init__(self,interpreter,debug=False):
        """ base class to write transform methods """
        Visitor.__init__(self)
        self.interpreter = interpreter
        self.top_ast = self.interpreter.ast
        self.lexer = self.interpreter.lexer    
        self.debug = debug
        if ( self.debug ):
             print(unicode(self.top_ast))
        self.top_ast.visit(self)
        
    def update_line(self,obj):
        pass
        return
        
    def visit_identifier(self, IDobj):  
        # unicode(IDobj.id)
        return
    
    def visit_string(self, string):
        # string
        return
    
    def visit_number(self, num):
        # num
        return
    
    def visit_expr_call(self,expr_call):
        expr_call.func_id.visit(self)
        expr_call.arglist.visit(self)
        return

    def visit_expr_list(self, expr_list):
        for pos,exp_itr in enumerate(expr_list.exprs):
            exp_itr.visit( self )
            
        return
    
    def visit_stmt_list(self,stmt_list):
        for stmt in stmt_list.List:
            stmt.visit(self)
        return
    
    def visit_stmt( self, stmt):
        ## is this a recipe for getting stuck in a loop?
        stmt.visit(self)
        return
    
    def visit_expr(self, expr):
        if expr.term: expr.term.visit(self)
        toktype = EzhilToken.token_types[expr.binop.kind]
        if expr.next_expr: expr.next_expr.visit(self)
        return
    
    def visit_return_stmt(self, ret_stmt):
        keyword = u"பின்கொடு"
        # return may have optional argument
        if hasattr(ret_stmt.rvalue,'visit'):
            ret_stmt.rvalue.visit(self)
        return
    
    def visit_break_stmt(self, break_stmt ):
        keyword = u"நிறுத்து" #EzhilToken.Keywords["break"]
        return
    
    def visit_continue_stmt(self, cont_stmt):
        keyword = u"தொடர்" #EzhilToken.Keywords["continue"]
        return
    
    def visit_else_stmt(self,else_stmt):
        keyword = u"இல்லை"
        if else_stmt.stmt: else_stmt.stmt.visit( self )
        return
    
    def visit_if_elseif_stmt(self,if_elseif_stmt):
        # condition expression
        if if_elseif_stmt.expr: if_elseif_stmt.expr.visit(self)
        
        # IF kw
        keyword_if = u"ஆனால்"
        
        # True-Body
        if if_elseif_stmt.body: if_elseif_stmt.body.visit( self )
        
        # False-Body - optionally present
        if hasattr(if_elseif_stmt.next_stmt,'visit'):
            if_elseif_stmt.next_stmt.visit(self)
        
        self.visit_end_kw()
        
    def visit_end_kw(self):
        # END kw
        keyword_end = u"முடி"
        
    def visit_while_stmt(self,while_stmt):
        """
        @( itr < L ) வரை
                        சமம்= சமம் + input[itr]*wts[itr]
            itr = itr + 1
                முடி"""        
        # condition expression
        if while_stmt.expr: while_stmt.expr.visit(self)
        
        # While kw
        keyword_while = u"வரை"
        
        # Body
        if while_stmt.body: while_stmt.body.visit( self )
        
        self.visit_end_kw()
        return
    
    # foreach is transformed at the AST-level
    # so its really a MACRO here
    def visit_for_stmt(self,for_stmt):
        """
        @( x = -1 , x < 0, x = x + 1 ) ஆக
                        பதிப்பி x, "கருவேபில"
                முடி
        """
        
        # condition expression
        if for_stmt.expr_init:
            for_stmt.expr_init.visit(self)
        if for_stmt.expr_cond:
            for_stmt.expr_cond.visit(self)
        if for_stmt.expr_update:
            for_stmt.expr_update.visit(self)
        
        # For kw
        keyword_for = u"ஆக"
        # Body
        if for_stmt.body:
            for_stmt.body.visit( self )
        self.visit_end_kw()
        return

    def visit_assign_stmt(self, assign_stmt):
        if assign_stmt.lvalue:
            assign_stmt.lvalue.visit( self )
        if assign_stmt.rvalue:
            assign_stmt.rvalue.visit( self )
        return

    def visit_print_stmt(self, print_stmt):
        keyword = u"பதிப்பி"
        if print_stmt.exprlst:
            print_stmt.exprlst.visit(self)
        return

    def visit_eval_stmt(self, eval_stmt ):
        #print(u"==>%s/%s"%(eval_stmt.expr.__class__,unicode(eval_stmt)))
        if eval_stmt.expr:
            eval_stmt.expr.visit(self)
        return
    
    def visit_arg_list(self, arg_list):
        L = len(arg_list.get_list())
        for pos,arg in enumerate(arg_list.get_list()):
            if hasattr(arg,'visit'):
                arg.visit(self)
        return

    def visit_value_list(self,value_list):
        for value in value_list.args:
            value.visit(self)
        return

    def visit_function(self,fndecl_stmt):
        """
        நிரல்பாகம் fibonacci_தமிழ்( x )
        @( x <= 1 ) ஆனால்
                        ஈ = 1
                இல்லை
                        ஈ = fibonacci_தமிழ்( x - 1 ) + fibonacci_தமிழ்( x - 2 )
                முடி 
                பின்கொடு ஈ
        முடி
        """
        
        # Function kw
        keyword_fn = u"நிரல்பாகம்"
        
        # name of function
        
        # arglist expression
        if fndecl_stmt.arglist:
            fndecl_stmt.arglist.visit(self)
        
        # Body expression
        if fndecl_stmt.body:
            fndecl_stmt.body.visit(self)
        
        return
    
    def visit_binary_expr(self,binexpr):
        self.visit_expr(binexpr)
        return
    