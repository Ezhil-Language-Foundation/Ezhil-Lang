#!/usr/bin/python
##This Python file uses the following encoding: utf-8
##
## (C) 2008 Muthiah Annamalai,
## Licensed under GPL Version 3
## 
## Module has elements of PARSE-TREE  AST 
## class TreeWalker

## Visitor template
class TreeWalker:
    def __init__(self):
        """ initialize data structures"""
        # self.codegen, pretty-printer, 
        # tree-source-transformer etc.
        
    def visit_identifier(self, id):  
        ## do something for id
        return

    def visit_string(self, str):
        return

    def visit_number(self, num):
        return

    def visit_expr_call(self,expr_call):
        return

    def visit_expr_list(self, expr_list):
        return

    def visit_stmt( self, stmt):
        return

    def visit_expr(self, expr):
        return

    def visit_return_stmt(self, ret_stmt):
        return

    def visit_break_stmt(self, break_stmt ):
        return

    def visit_continue_stmt(self, cont_stmt):
        return

    def visit_else_stmt(self,else_stmt):
        return

    def visit_if_elseif_stmt(self,if_elseif_stmt):
        return

    def visit_while_stmt(self,stmt):
        return

    def visit_for_stmt(self,for_stmt):
        return

    def visit_assign_stmt(self, assign_stmt):
        return

    def visit_print_stmt(self, print_stmt):
        return

    def visit_eval_stmt(self, eval_stmt ):
        return

    def visit_arg_list(self, arg_list):
        return

    def visit_value_list(self,value_list):
        return

    def visit_stmt_list(self,stmt_list):
        return

    def visit_function(self,function):
        return

    def visit_program_or_script(self):
        ## entry point
        return

