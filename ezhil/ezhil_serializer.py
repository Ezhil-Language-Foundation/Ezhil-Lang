#!/usr/bin/python
##This Python file uses the following encoding: utf-8
##
## (C) 2008-2015 Muthiah Annamalai,
## Licensed under GPL Version 3
## 
## Module has elements of PARSE-TREE  AST 
## 
import codecs
import functools
import sys

from .ezhil_scanner import EzhilToken, Token
from .transform import TransformVisitor

PYTHON3 = (sys.version[0] == '3')
if PYTHON3:
    unicode = str

try:
    import graphviz as gv

    graph = functools.partial(gv.Graph, format='svg')
    digraph = functools.partial(gv.Digraph, format='svg')
except ImportError as ie:
    pass

import xml.sax.saxutils

class Tag(object):
    def __init__(self,fileobj,name,tab=0,attrs={}):
        object.__init__(self)
        self.tagname = name
        self.attrs = attrs
        self.fileobj = fileobj
        self.tabstr = u" "*tab
        if len(attrs) > 0:
            pfx = u" "
        else:
            pfx = u""
        serialized_attrs = pfx+u" ".join( [ u"%s=\"%s\" "%(unicode(k),unicode(v)) for k,v in attrs.items()])
        self.fileobj.write(u"%s<%s%s>\n"%(self.tabstr,self.tagname,serialized_attrs))
    
    def disp(self,content):
        self.fileobj.write(u"%s\n"%content)
    
    def __del__(self):
        self.fileobj.write(u"%s</%s>\n"%(self.tabstr,self.tagname))
    
class SerializerXML(TransformVisitor):
    def __init__(self,interpreter,debug=False,filename=None):
        """ base class to write transform methods """
        self.tab = 0
        self.filename = filename
        self.file = sys.stdout
        if filename:
           self.file = codecs.open(filename,"w","UTF-8")
        self.file.write(u"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
        tobj = Tag(self.file,u"ezhil",self.tab)
        self.incr()
        TransformVisitor.__init__(self,interpreter,debug)
        self.decr()
    
    def __del__(self):
        if self.filename:
            self.file.close()
        
    def disp_basic(self,tagname,contents):
        escaped_contents =  xml.sax.saxutils.escape(u"%s"%contents)
        self.file.write(u"%s<%s>%s</%s>\n"%(self.tabstr(),tagname,escaped_contents,tagname))
    
    def tabstr(self):
        return u" "*self.tab
        
    def incr(self):
        self.tab += 1
    
    def decr(self):
        self.tab -= 1

    def update_line(self,obj):
        pass
        return
        
    def visit_identifier(self, IDobj):  
        self.disp_basic( u"ID",unicode(IDobj.id))
        return
    
    def visit_string(self, string):
        self.disp_basic( u"STR",string)
        return
    
    def visit_number(self, num):
        self.disp_basic( u"NUM",num)
        return
    
    def visit_expr_call(self,expr_call):
        tobj = Tag(self.file,name=u"EXPRCALL",tab=self.tab)
        self.incr()

        tobj_id = Tag(self.file,name=u"FUNCID",tab=self.tab)
        self.incr()
        expr_call.func_id.visit(self)
        del tobj_id
        self.decr()
        
        self.incr()
        tobj_args = Tag(self.file,name=u"FUNCARGS",tab=self.tab)
        expr_call.arglist.visit(self)
        del tobj_args
        self.decr()
        
        self.decr()
        return
    
    def visit_expr_list(self, expr_list):
        tobj = Tag(self.file,name=u"EXPRLIST",tab=self.tab)
        self.incr()
        for pos,exp_itr in enumerate(expr_list.exprs):
            exp_itr.visit( self )
        self.decr()
        return
    
    def visit_stmt_list(self,stmt_list):
        tobj = Tag(self.file,name=u"STMTLIST",tab=self.tab)
        self.incr()
        for stmt in stmt_list.List:
            stmt.visit(self)
        self.decr()
        return
    
    def visit_stmt( self, stmt):
        tobj = Tag(self.file,name=u"STMT",tab=self.tab)
        ## is this a recipe for getting stuck in a loop?
        stmt.visit(self)
        return
    
    def visit_expr(self, expr):
        escaped_tok_kind = xml.sax.saxutils.escape( Token.get_name(expr.binop.kind) )
        tobj = Tag(self.file,name=u"EXPR",tab=self.tab,attrs={u"binop":escaped_tok_kind})
        self.incr()
        
        tobj_term = Tag(self.file,name=u"TERM",tab=self.tab)
        self.incr()
        expr.term.visit(self)
        del tobj_term
        self.decr()
        
        toktype = EzhilToken.token_types[expr.binop.kind]
        expr.next_expr.visit(self)
        self.decr()
        return
    
    def visit_return_stmt(self, ret_stmt):
        tobj = Tag(self.file,name=u"RETURN",tab=self.tab)
        keyword = u"பின்கொடு"
        # return may have optional argument
        if hasattr(ret_stmt.rvalue,'visit'):
            ret_stmt.rvalue.visit(self)
        return
    
    def visit_break_stmt(self, break_stmt ):
        tobj = Tag(self.file,name=u"BREAK",tab=self.tab)
        keyword = u"நிறுத்து" #EzhilToken.Keywords["break"]
        return
    
    def visit_continue_stmt(self, cont_stmt):
        tobj = Tag(self.file,name=u"CONTINUE",tab=self.tab)
        keyword = u"தொடர்" #EzhilToken.Keywords["continue"]
        return
    
    def visit_else_stmt(self,else_stmt):
        tobj = Tag(self.file,name=u"ELSE",tab=self.tab)
        self.incr()
        keyword = u"இல்லை"
        else_stmt.stmt.visit( self )
        self.decr()
        return
    
    def visit_if_elseif_stmt(self,if_elseif_stmt):
        tobj = Tag(self.file,name=u"IF",tab=self.tab)
        self.incr()
        
        # condition expression
        if_elseif_stmt.expr.visit(self)
        
        # IF kw
        keyword_if = u"ஆனால்"
        
        # True-Body
        if_elseif_stmt.body.visit( self )
        
        # False-Body - optionally present
        if hasattr(if_elseif_stmt.next_stmt,'visit'):
            tobj_else = Tag(self.file,name=u"ELSE",tab=self.tab)
            self.incr()
            if_elseif_stmt.next_stmt.visit(self)
            del tobj_else
            self.decr()
        
        self.visit_end_kw()
        self.decr()
        
    def visit_end_kw(self):
        # END kw
        #tobj = Tag(name="END",tab=self.tab)
        keyword_end = u"முடி"
        
    def visit_while_stmt(self,while_stmt):
        """
        @( itr < L ) வரை
                        சமம்= சமம் + input[itr]*wts[itr]
            itr = itr + 1
                முடி"""
        tobj_while = Tag(self.file, name="WHILE", tab=self.tab)
        self.incr()

        # condition expression
        tobj_while_cond = Tag(self.file,name=u"WHILE_COND",tab=self.tab)
        self.incr()
        while_stmt.expr.visit(self)
        self.decr()
        del tobj_while_cond
        
        # While kw
        keyword_while = u"வரை"
        
        # Body
        while_stmt.body.visit( self )
        
        self.visit_end_kw()
        self.decr()
        return
    
    # foreach is transformed at the AST-level
    # so its really a MACRO here
    def visit_for_stmt(self,for_stmt):
        """
        @( x = -1 , x < 0, x = x + 1 ) ஆக
                        பதிப்பி x, "கருவேபில"
                முடி
        """
        tobj_for = Tag(self.file,name=u"FOR",tab=self.tab)
        self.incr()
        
        # condition expression
        tobj_for_init = Tag(self.file,name=u"FOR_INIT",tab=self.tab)
        for_stmt.expr_init.visit(self)
        del tobj_for_init
        
        tobj_for_cond = Tag(self.file,name=u"FOR_COND",tab=self.tab)
        for_stmt.expr_cond.visit(self)
        del tobj_for_cond
        
        tobj_for_update = Tag(self.file,name=u"FOR_UPDATE",tab=self.tab)
        for_stmt.expr_update.visit(self)
        del tobj_for_update
        
        # For kw
        keyword_for = u"ஆக"
        
        # Body
        for_stmt.body.visit( self )
        self.visit_end_kw()
        self.decr()
        return
    
    def visit_assign_stmt(self, assign_stmt):
        tobj_assign = Tag(self.file,name=u"ASSIGN",tab=self.tab)
        self.incr()
        
        tobj_assign_lval = Tag(self.file,name=u"ASSIGN_LVAL",tab=self.tab)
        self.incr()
        assign_stmt.lvalue.visit( self )
        self.decr()
        del tobj_assign_lval
        
        tobj_assign_rval = Tag(self.file,name=u"ASSIGN_RVAL",tab=self.tab)
        self.incr()
        assign_stmt.rvalue.visit( self )
        self.decr()
        del tobj_assign_rval
        
        self.decr()
        return
    
    def visit_print_stmt(self, print_stmt):
        tobj = Tag(self.file,name=u"PRINT",tab=self.tab)
        keyword = u"பதிப்பி"
        self.incr()
        print_stmt.exprlst.visit(self)
        self.decr()
        return

    def visit_eval_stmt(self, eval_stmt ):
        tobj = Tag(self.file,name=u"EVALSTMT",tab=self.tab)
        self.incr()
        eval_stmt.expr.visit(self)
        self.decr()
        return
    
    def visit_arg_list(self, arg_list):
        tobj = Tag(self.file,name=u"ARGLIST",tab=self.tab)
        self.incr()
        L = len(arg_list.get_list())
        for pos,arg in enumerate(arg_list.get_list()):
            if hasattr(arg,'visit'):
                arg.visit(self)
        self.decr()
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
        tobj = Tag(self.file,name=u"FUNCTION",tab=self.tab,attrs={u"name":fndecl_stmt.name})
        
        # Function kw
        keyword_fn = u"நிரல்பாகம்"
        
        # name of function
        
        # arglist expression
        fndecl_stmt.arglist.visit(self)
        
        # Body expression
        fndecl_stmt.body.visit(self)
        
        return
    
    def visit_binary_expr(self,binexpr):
        self.visit_expr(binexpr)
        return
    