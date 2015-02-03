#!/usr/bin/python
##This Python file uses the following encoding: utf-8
##
## (C) 2008 Muthiah Annamalai,
## Licensed under GPL Version 3
## 
## Module has elements of PARSE-TREE  AST 
## 

## Visitor template
class Visitor:
    def __init__(self):
        """ initialize data structures"""
        # self.codegen, pretty-printer, 
        # tree-source-transformer etc.

    def default(self,*args):
        raise Exception(u'Not Implemented')
    
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

    def visit_program_or_script(self):
        ## entry point
        return
