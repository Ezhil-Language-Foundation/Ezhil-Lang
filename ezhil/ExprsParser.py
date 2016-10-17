#!/usr/bin/python
##
## (C) 2007, 2008 Muthiah Annamalai,
## Licensed under GPL Version 3
## 
## parser & AST  use the parsing frontend and 
## AST elements to build the parse tree.
## Class Parser

from math import *
import copy
import os
import sys
import string
import inspect

PYTHON3 = (sys.version[0] == '3')
if PYTHON3:
    unicode = str

## scanner for exprs language
from .scanner import Token, Lexeme, Lex

## exceptions
from .errors import RuntimeException, ParseException

## runtime elements
from .runtime import  Environment, BuiltinFunction, \
 BlindBuiltins, DebugUtils

## AST elements
from .ast import Expr, ExprCall, ExprList, Stmt, ReturnStmt, \
 BreakStmt, ContinueStmt, ElseStmt, IfStmt, WhileStmt, \
 ForStmt, AssignStmt, PrintStmt, EvalStmt, ArgList, \
 ValueList, Function, StmtList, Identifier, Number, \
 String

## Parser implementes the grammar for 'exprs' language.
## Entry point is parse(), after appropriate ctor-setup.
class Parser(DebugUtils):
    """ when you add new language feature, add a AST class 
    and its evaluate methods. Also add a parser method """
    def __init__(self,lexer,fcn_map, builtin_map, dbg = False):
        DebugUtils.__init__(self,dbg)
        self.parsing_function = False
        self.lex=lexer
        self.ast=None
        self.currently_parsing = [] # stack, just in case we should have parse errors
        self.function_map = fcn_map #parsed functions
        self.builtin_map = builtin_map #pointers to builtin functions
        self.if_stack = [] #parsing if-statements
        self.loop_stack = [] #parsing while-statements
        self.last_tok = None ## handle to last token dequeued
        self.inside_if = False
    
    def reset(self):
        """reset parser, and lexer, when stuff gets messed up"""
        self.inside_if = False
        self.loop_stack = []
        self.if_stack = []
        self.currently_parsing = []
        self.lex.reset()
        return
	
    def check_loop_stack(self):
        if ( len(self.loop_stack) == 0 ):
            raise ParseException(u"break/continue statement outside any loop, near" + str(self.last_token()));
        return len(self.loop_stack);

    def check_if_stack(self):
        if ( len(self.if_stack) == 0 ):
            raise ParseException(u"unmatched else statement, near" + str(self.last_token()))
        return len(self.if_stack)

    def last_token(self):
        return self.last_tok

    def peek(self):
        ptok = self.lex.peek()        
        self.dbg_msg(u"peek: " + unicode(ptok))
        return ptok

    def dequeue(self):
        tok = self.lex.dequeue()
        self.last_tok = tok
        self.dbg_msg( u"deqeue: " + unicode(tok) )
        return tok

    def match(self,kind):
        ## if match return token, else ParseException
        tok = self.dequeue()
        if ( tok.kind != kind ):
            raise ParseException(u"cannot find token "+ \
                                Token.get_name(kind) + u" got " \
                                + unicode(tok) + u" instead!")
        return tok

    def __repr__(self):
        rval =  u"[Interpreter: "
        rval = rval + u"[Functions["
        for k in list(self.function_map.keys()):
            rval = rval + u"\n "+ str(self.function_map[k]) 
        rval = rval + u"]] "+ str(self.ast) + u"]\n"
        return rval

    def warn_function_overrides( self, func_name ):
        ## used in defining user-functions to see
        ## if they shadow builtins.
        val =  ( func_name in self.function_map )
        if ( val ):
            raise Exception(u"ERROR: function %s is multiply defined"%(func_name))
        if func_name in self.builtin_map :
            raise Exception(u"ERROR: function %s overrides builtin"%(func_name))
        return val
    
    def parse(self):
        """ parser routine """
        self.ast = StmtList()
        while ( not self.lex.end_of_tokens() ):
            self.dbg_msg( "AST length = %d"%len(self.ast) )
            if ( self.lex.peek().kind == Token.DEF ):
                self.dbg_msg ( "parsing for function" )
                ## save function in a global table.
                func = self.function()
                self.warn_function_overrides(func.name)
                self.function_map[func.name]=func
            else:
                self.dbg_msg( "parsing for stmt" )
                st = self.stmt()
                if ( not self.parsing_function ):
                    self.ast.append(st)
        return self.ast


    def stmtlist(self):
        """ parse a bunch of statements """
        self.dbg_msg(" STMTLIST ")
        stlist = StmtList()
        while( not self.lex.end_of_tokens() ):
            self.dbg_msg("STMTLIST => STMT")
            ptok = self.peek()            
            if ( ptok.kind == Token.END ):
                break
            if ( not self.inside_if and 
                 ( ptok.kind == Token.ELSE
                   or ptok.kind == Token.ELSEIF ) ):
                break
            st = self.stmt()
            stlist.append( st )
        return stlist
    
    def stmt(self):
        """ try an assign, print, return, if or eval statement """
        self.dbg_msg(" STMT ")
        ptok = self.peek()
        self.dbg_msg("stmt: peeking at "+unicode(ptok))
        if ( ptok.kind == Token.RETURN ): 
            ## return <expression>
            ret_tok = self.dequeue()
            [l,c]=ret_tok.get_line_col();
            rstmt = ReturnStmt(self.expr(),l,c,self.debug)
            self.dbg_msg("return statement parsed")
            return rstmt
        elif ( ptok.kind == Token.PRINT ):
            ## print <expression>
            print_tok = self.dequeue()
            [l,c]=print_tok.get_line_col();
            return PrintStmt(self.exprlist(),l,c,self.debug)
        elif ( ptok.kind == Token.IF ):
            ## if <expression> stmtlist end
            if_tok = self.dequeue()
            [l,c]=if_tok.get_line_col();
            exp = self.expr()
            ifstmt = IfStmt( exp, None, None, l, c, self.debug)
            self.if_stack.append(ifstmt)
            body = self.stmtlist()
            ifstmt.set_body( body )
            ptok = self.peek()
            if ( ptok.kind in [Token.ELSEIF, Token.ELSE] ):
                self.inside_if = True
                next_stmt = self.stmtlist()
                self.inside_if = False
                ifstmt.append_stmt( next_stmt )
            self.match(Token.END)
            return ifstmt
        elif ( ptok.kind == Token.ELSEIF ):
            ## elseif <expression> stmtlist
            elseif_tok = self.dequeue()
            [l,c]=elseif_tok.get_line_col();
            self.check_if_stack()
            exp = self.expr()
            elseif_stmt = IfStmt( exp, None, None, l, c, self.debug )
            ifstmt = self.if_stack[-1]
            ifstmt.append_stmt( elseif_stmt )
            self.if_stack.pop()
            self.if_stack.append( elseif_stmt )
            body = self.stmtlist( )
            elseif_stmt.set_body ( body )
            return elseif_stmt
        elif ( ptok.kind == Token.ELSE ):
            ## else stmtlist
            self.check_if_stack()
            ifstmt = self.if_stack.pop()
            self.dbg_msg("stmt-else: ")
            else_tok = self.dequeue()
            [l,c]=else_tok.get_line_col()
            body = self.stmtlist()
            else_stmt = ElseStmt( body , l, c, self.debug)
            ifstmt.append_stmt( else_stmt )
            return else_stmt
        elif ( ptok.kind == Token.FOR ):
            ## Fixme : empty for loops not allowed.
            """ For ( exp1 ; exp2 ; exp3 ) stmtlist  end"""
            self.loop_stack.append(True)
            self.dbg_msg("for-statement")
            for_tok = self.dequeue()
            self.match(Token.LPAREN)

            lhs = self.expr()
            init = lhs 
            ptok = self.peek()
            if ( ptok.kind in Token.ASSIGNOP ):
                assign_tok = self.dequeue()
                [l,c]=assign_tok.get_line_col();
                rhs = self.expr()
                init = AssignStmt( lhs, assign_tok, rhs, l, c, self.debug)

            self.match(Token.COMMA )

            cond = self.expr();
            self.match(Token.COMMA )

            lhs = self.expr()
            update = lhs 
            ptok = self.peek()
            if ( ptok.kind in Token.ASSIGNOP ):
                assign_tok = self.dequeue()
                [l,c]=assign_tok.get_line_col()
                rhs = self.expr()
                update = AssignStmt( lhs, assign_tok, rhs, l, c, self.debug)

            
            self.match(Token.RPAREN);
            body = self.stmtlist( )
            self.match(Token.END)
            [l,c]= for_tok.get_line_col();
            forstmt = ForStmt(init, cond, update, body, l, c, self.debug);
            self.loop_stack.pop();
            return forstmt
        elif ( ptok.kind == Token.WHILE ):
            ## while ( expr ) body end
            self.loop_stack.append(True);
            self.dbg_msg("while-statement");
            while_tok = self.dequeue();
            [l,c]=while_tok.get_line_col()
            wexpr = self.expr();
            body = self.stmtlist( )
            self.match(Token.END)
            whilestmt = WhileStmt(wexpr, body, l, c, self.debug);
            self.loop_stack.pop();
            return whilestmt
        elif ( ptok.kind == Token.BREAK ):
            ## break, must be in loop-environment
            self.dbg_msg("break-statement");
            break_tok = self.dequeue();
            [l,c]=break_tok.get_line_col()
            self.check_loop_stack(); ##raises a parse error
            brkstmt = BreakStmt( l, c, self.debug);
            return brkstmt

        elif ( ptok.kind == Token.CONTINUE ):
            ## continue, must be in loop-environment
            self.dbg_msg("continue-statement");
            cont_tok = self.dequeue();
            [l,c]=cont_tok.get_line_col()
            self.check_loop_stack(); ##raises a parse error
            cntstmt = ContinueStmt( l, c, self.debug);
            return cntstmt

        else:
            ## lval := rval
            ptok = self.peek()
            [l,c] = ptok.get_line_col()
            lhs = self.expr()
            self.dbg_msg("parsing expr: "+str(lhs))
            ptok = self.peek()
            if ( ptok.kind in Token.ASSIGNOP ):
                assign_tok = self.dequeue()
                rhs = self.expr()
                [l,c]=assign_tok.get_line_col()
                return AssignStmt( lhs, assign_tok, rhs, l, c, self.debug)
            return EvalStmt( lhs, l, c, self.debug )
        raise ParseException("parsing Statement, unkown operators" + unicode(ptok))
    
    def function(self):
        """ def[kw] fname[id] (arglist) {body} end[kw] """
        if ( self.parsing_function ):
            raise ParseException(" Nested functions not allowed! ")

        self.parsing_function = True
        def_tok = self.dequeue()
        if ( def_tok.kind != Token.DEF ):
            raise ParseException("unmatched 'def'  in function " +str(def_tok))
        
        id_tok = self.dequeue()
        if ( id_tok.kind != Token.ID ):
            raise ParseException("expected identifier in function"+str(id_tok))
        
        arglist = self.arglist()
        self.dbg_msg( "finished parsing arglist" )
        body = self.stmtlist()

        self.match( Token.END )
        [l,c] = def_tok.get_line_col()
        fval = Function( id_tok.val, arglist, body, l, c, self.debug )
        self.parsing_function = False
        self.dbg_msg( "finished parsing function" ) 
        return fval

    def valuelist(self):
        """parse: ( expr_1 , expr_2, ... ) """
        valueList = list()
        self.dbg_msg("valuelist: ")
        lparen_tok = self.match( Token.LPAREN )
        while ( self.peek().kind != Token.RPAREN ):
            val = self.expr()
            self.dbg_msg("valuelist-expr: "+str(val))
            valueList.append( val )
            ptok = self.peek()
            if  ( ptok.kind == Token.RPAREN ):
                break
            elif ( ptok.kind == Token.COMMA ):
                self.match( Token.COMMA )
            else:
                raise ParseException(" function call argument list "+unicode(ptok))
        self.match( Token.RPAREN )
        [l,c] = lparen_tok.get_line_col()
        return ValueList(valueList, l, c, self.debug )


    def arglist(self):
        """parse: ( arg_1, arg_2, ... ) """
        self.dbg_msg( " ARGLIST " )
        args = list()
        lparen_tok = self.match( Token.LPAREN )
        while ( self.peek().kind != Token.RPAREN ):
            arg_name = self.dequeue()
            args.append( arg_name.val )
            ptok = self.peek()
            if  ( ptok.kind == Token.RPAREN ):
                break
            elif ( ptok.kind == Token.COMMA ):
                self.match( Token.COMMA )
            else:
                raise ParseException(" function definition argument list "
                                     +unicode(ptok))
        self.match( Token.RPAREN )
        [l,c] = lparen_tok.get_line_col()
        return ArgList(args , l, c, self.debug )
        
    def exprlist(self):
        """   EXPRLIST : EXPR, EXPRLIST        
        ##  EXPRLIST : EXPR """
        self.dbg_msg( " EXPRLIST " )
        exprs=[]
        comma_tok = None
        l = 0; c = 0
        while ( not self.lex.end_of_tokens() ):
            exprs.append(self.expr())
            if self.lex.peek().kind != Token.COMMA:
                break            
            tok = self.match(Token.COMMA)
            if ( not comma_tok ):
                comma_tok = tok 

        if ( comma_tok ):
            [l,c] = comma_tok.get_line_col()
        self.dbg_msg("finished expression list")
        return ExprList(exprs, l, c, self.debug)


    def expr(self):
        self.dbg_msg( " EXPR " )
        val1=self.term()
        res=val1
        ptok = self.peek()
        if ptok.kind in Token.ADDSUB:
            binop=self.dequeue()
            val2=self.expr()
            [l,c] = binop.get_line_col()
            res=Expr(val1,binop,val2, l, c, self.debug )
        elif ptok.kind == Token.LPAREN:
            ## function call -OR- array type.
            if ( res.__class__ != Identifier ):
                raise ParseException("invalid function call"+unicode(ptok))
            [l,c] = ptok.get_line_col()
            vallist = self.valuelist()
            res=ExprCall( res, vallist, l, c, self.debug )
        return res

    def term(self):
        """ this is a grammar abstraction; 
        but AST only has Expr elements"""
        self.dbg_msg( "term" )
        val1=self.factor()
        res=val1

        tok = self.peek()
        if ( tok.kind in Token.MULDIV 
             or  tok.kind in Token.COMPARE 
             or tok.kind in Token.EXPMOD  ):
            binop=self.dequeue()
            val2=self.expr()
            [l,c] = binop.get_line_col()
            res=Expr(val1,binop,val2, l, c, self.debug)

        return res
    
    def factor(self):
        self.dbg_msg( "factor" )
        tok=self.peek()
        if tok.kind == Token.LPAREN:
            lparen_tok = self.dequeue()
            val=self.expr()
            if self.dequeue().kind!=Token.RPAREN:
                raise SyntaxError("Missing Parens")
        elif tok.kind == Token.NUMBER:
            tok_num = self.dequeue()
            [l, c] = tok_num.get_line_col()
            val = Number( tok.val , l, c, self.debug )
        elif tok.kind == Token.ID:
            tok_id = self.dequeue()
            [l, c] = tok_id.get_line_col()
            val = Identifier( tok.val , l, c, self.debug )
            ptok = self.peek()
            self.dbg_msg("factor: "+unicode(ptok) + " / "+str(tok) )
            if ( ptok.kind == Token.LPAREN ):
                ## function call
                [l, c] = ptok.get_line_col()
                vallist = self.valuelist()
                val=ExprCall( val, vallist, l, c, self.debug )
            elif ( ptok.kind == Token.LSQRBRACE ):
                ## array type
                val=None
                raise ParseException("arrays not implemented"+unicode(ptok));
        elif tok.kind == Token.STRING :
            str_tok = self.dequeue()
            [l,c] = str_tok.get_line_col()
            val = String( tok.val , l, c, self.debug )
        else:
            raise ParseException("Expected Number, found something "+str(tok))
        
        self.dbg_msg( "factor-returning: "+str(val) )
        return val
