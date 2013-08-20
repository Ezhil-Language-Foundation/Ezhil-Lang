#!/usr/bin/python
## -*- coding: utf-8 -*-
## 
## (C) 2008, 2013 Muthiah Annamalai
## Licensed under GPL Version 3
## 
## This module is the pretty-printer for the Ezhil language.
## It contains classes @WikiStyle, @Printer
## 

from theme import XsyTheme
from ezhil_scanner import EzhilLex, EzhilToken
from ezhil import EzhilInterpreter
from transform import Visitor

class WikiStyle:
    @staticmethod
    def wrap_msg(attrib,text):
        """ @text is any character stream that has to be wrapper in a style-Theme,
            specified by @attrib """
        if ( len(attrib) >= 1 ):
            out = '<span style="color:#'+attrib[0]
        if ( len(attrib) >= 2 ):
            out = out + ';background:#'+attrib[1]
        out = out + '">' + attrib.process(text) + "</span>"
        return out

class Printer(Visitor):
    def __init__(self,src_file):
        """ @styler uses a Wiki/HTML/LaTeX output formatter, with a color theme 
        specificied by @theme to render the text into the appropriate format"""
        Visitor.__init__(self)
        self.styler = WikiStyle.wrap_msg
        self.theme = XsyTheme()
        self.lexer = EzhilLex(src_file)
    
    def default(self,*args):
        """ /dev/zero dump for all visitor methods when not handled in derived class"""
        #args[0] is AST object
        print "def :",str(args[0])
        
    def visit_identifier(self, id):  
        attrib = self.theme.Variables
        print self.styler(attrib,str(id))
        return
    
    def visit_string(self, string):
        attrib = self.theme.LiteralString
        print self.styler(attrib,str(string))
        return

    def visit_number(self, num):
        attrib = self.theme.LiteralNumber
        print self.styler(attrib,str(num))
        return

    def visit_expr_call(self,expr_call):
        var_attrib = self.theme.Variables
        print self.styler(var_attrib,str(expr_call.func_id.id))
        op_attrib = self.theme.Operators
        print self.styler(op_attrib,"(")
        expr_call.arglist.visit( self )
        print self.styler(op_attrib,")")
        return

    def visit_expr_list(self, expr_list):
        for exp_itr in expr_list.exprs:
            exp_itr.visit( self )
        return

    def visit_stmt_list(self,stmt_list):
        for stmt in stmt_list.List:
            stmt.visit(self)
        return

    def visit_stmt( self, stmt):
        print "visit //"
        stmt.visit(self)
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
        kw_attrib = self.theme.Keywords
        keyword = "பதிப்பி"
        print self.styler(kw_attrib,str(keyword))
        print_stmt.exprlst.visit(self)
        return

    def visit_eval_stmt(self, eval_stmt ):
        eval_stmt.expr.visit(self)
        return

    def visit_arg_list(self, arg_list):
        self.default(arg_list)
        return

    def visit_value_list(self,value_list):
        for value in value_list.args:
            value.visit(self)
        return

    def visit_function(self,function):
        self.default(function)
        return
    
    def pretty_print(self):
        self.parse_eval = EzhilInterpreter(self.lexer)
        ast = self.parse_eval.parse()
        print ast
        ast.visit(self)
    
    # method walks the lexer-tokens and calls the appropriate elements
    # basic lexical hiliting
    def lexical_hilite(self):
        self.lexer.tokens.reverse()
        out = []
        for t in self.lexer.tokens:
            add_br = False
            attrib = self.theme.Operators
            if EzhilToken.is_keyword(t.kind):
                attrib = self.theme.Keywords
                if ( EzhilToken.get_name(t.kind) in ["END", "ELSE"] ):
                    out.append('<BR />\n')
            elif EzhilToken.is_number(t.kind):
                attrib = self.theme.LiteralNumber
            elif EzhilToken.is_string(t.kind):
                attrib = self.theme.LiteralString
                t.val = '"'+t.val+'"' #FIXME: ideally do some escaping as well
            elif EzhilToken.is_id(t.kind):
                attrib = self.theme.Variables
            elif( t.val in ["@", "பதிப்பி" ] ):
                attrib = self.theme.Builtins
                out.append('<BR />\n')
            
            t.val = " " + str(t.val)
            out.append( self.styler(attrib,t.val) )
            if ( add_br ):
                out.append("<BR />\n")
        
        return "".join(out)

if __name__ == "__main__":
    from sys import argv,exit
    if len(argv) <= 1:
        print "usage: python ezhil/prettify.py <file1> <file2> ... "
        exit(-1)
    for aFile in argv[1:]:
        print "working with ",aFile
        Printer(aFile).pretty_print()
    
