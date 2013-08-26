#!/usr/bin/python
##
## (C) 2007, 2008 Muthiah Annamalai,
## Licensed under GPL Version 3
## 
## parser & AST  use the parsing frontend and 
## AST elements to build the parse tree.
## Class Parser
##
## ezhil parser & AST builder
## use the parsing frontend and similar
## AST elements from the previous classes
## TODO: extract scanner and AST members into a module for sharing.
## and use them here.

import copy
import os, sys, string, inspect

## scanner for Ezhil language
from ezhil_scanner import EzhilToken, EzhilLex, EzhilLexeme

## exceptions
from errors import RuntimeException, ParseException

## runtime elements
from runtime import  Environment, BuiltinFunction, \
 BlindBuiltins, DebugUtils

## AST elements
from ast import Expr, UnaryExpr, ExprCall, ExprList, Stmt, ReturnStmt, \
 BreakStmt, ContinueStmt, ElseStmt, IfStmt, WhileStmt, DoWhileStmt, \
 ForStmt, AssignStmt, PrintStmt, EvalStmt, ArgList, \
 ValueList, Function, StmtList, Identifier, Number, \
 String, Array

## use exprs language parser
from ExprsParser import Parser

## Parser implementes the grammar for 'exprs' language.
## Entry point is parse(), after appropriate ctor-setup.
class EzhilParser(Parser):
    """ when you add new language feature, add a AST class 
    and its evaluate methods. Also add a parser method """
    def __init__(self,lexer,fcn_map, builtin_map, dbg = False):
        if ( not isinstance(lexer, EzhilLex) ):
                raise RuntimeException("Cannot find Ezhil lexer class")
        Parser.__init__(self,lexer,fcn_map,builtin_map,dbg)


    def factory(lexer,fcn_map,builtin_map, dbg = False):
        """ Factory method """
        return EzhilParser(lexer,fcn_map,builtin_map, dbg)
    factory = staticmethod(factory)

    def match(self,kind):
        ## if match return token, else ParseException
        tok = self.dequeue()
        if ( tok.kind != kind ):
            raise ParseException("cannot find token "+ \
                                 EzhilToken.get_name(kind) + " got " \
                                + str(tok)  \
                                + " instead!")
        return tok

    def parse(self):
        """ parser routine """
        self.ast = StmtList()
        while ( not self.lex.end_of_tokens() ):
            self.dbg_msg( "AST length = %d"%len(self.ast) )
            if ( self.lex.peek().kind ==  EzhilToken.DEF ):
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

    def stmtlist(self,pass_in_ATexpr=None):
        """ parse a bunch of statements """
        self.dbg_msg(" STMTLIST ")
        stlist = StmtList()
        while( not self.lex.end_of_tokens() ):
            self.dbg_msg("STMTLIST => STMT")
            ptok = self.peek()
            self.dbg_msg("STMTLIST "+str(ptok))
            if ( self.debug ): print("peek @ ",str(ptok))
            if ( ptok.kind == EzhilToken.END ):
                self.dbg_msg("End token found");
                break
            elif ( ptok.kind == EzhilToken.DOWHILE ):
                if ( self.debug ): print("DOWHILE token found")
                break            
            elif( self.inside_if and 
                 ( ptok.kind ==  EzhilToken.ELSE
                   or ptok.kind == EzhilToken.ATRATEOF 
                   or ptok.kind == EzhilToken.CASE 
                   or ptok.kind == EzhilToken.OTHERWISE ) ):
                break
            st = self.stmt(pass_in_ATexpr)
            pass_in_ATexpr = None
            stlist.append( st )
        return stlist
    
    def parseSwitchStmt(self,exp):
        ## @ <ID/EXPR> SWITCH @( expr ) CASE {stmtlist} @( expr ) CASE {stmtlist} OTHERWISE {stmtlist} END
        ## implement as an if-elseif-else statement
        self.dbg_msg("parsing SWITCH statement")
        sw_tok = self.dequeue()
        [l,c]=sw_tok.get_line_col()
        self.inside_if = True
        lhs=exp[0]
        # enter this if-statement always
        ifstmt = IfStmt( Number(1), None, None, l, c, self.debug)
        self.if_stack.append(ifstmt)
        self.dbg_msg("parsing SWITCH-body") #self.dbg_msg        
        ptok = self.peek()
        equality_token = EzhilLexeme("=",EzhilToken.EQUALITY)
        while ( ptok.kind == EzhilToken.ATRATEOF or ptok.kind == EzhilToken.OTHERWISE ):
            self.inside_if = True
            [l,c]=ptok.get_line_col()
            if ( ptok.kind == EzhilToken.ATRATEOF ):
                # parse elseif branch
                self.dbg_msg("parsing CASE")
                self.match( EzhilToken.ATRATEOF )
                exp = self.valuelist();
                self.dbg_msg("parsing CASE EXPR")
                self.match( EzhilToken.CASE )
                next_stmt = self.stmtlist()                
                expr = Expr( lhs, equality_token, exp[0], l, c, self.debug )
                self.dbg_msg("building an Expr "+str(expr))                
                if not ifstmt.body :
                    ifstmt.expr = expr
                    ifstmt.body = next_stmt
                else:
                    case_stmt = IfStmt(expr,next_stmt,None,l,c,self.debug);
                    ifstmt.append_stmt( case_stmt )
            elif ( ptok.kind == EzhilToken.OTHERWISE ):
                #parse else branch
                self.dbg_msg("parsing OTHERWISE: ")
                self.match( EzhilToken.OTHERWISE )
                self.dbg_msg("parsing OTHERWISE-Body")
                self.inside_if = False
                body = self.stmtlist()
                else_stmt = ElseStmt( body , l, c, self.debug)
                if not ifstmt.body :
                    ifstmt.body = else_stmt
                else:
                    ifstmt.append_stmt( else_stmt )
                break
            else:
                self.inside_if = False
                raise ParseException("SWITCH-CASE-OTHERWISE statement syntax is messed up")
            ptok = self.peek()
            self.dbg_msg("parsing SWITCH-CASE next bits "+str(ptok))
        self.match( EzhilToken.END )
        self.inside_if = False
        self.dbg_msg("parsing -SWITCH-CASE- complete")
        return ifstmt
    
    def parseIfStmt(self,exp):
        ## @ <expression> if { stmtlist } @<expr> ELSEIF {stmtlist} ELSE <stmtlist> END
        self.dbg_msg("parsing IF statement")
        if_tok = self.dequeue()
        [l,c]=if_tok.get_line_col()
        self.inside_if = True
        ifstmt = IfStmt( exp[0], None, None, l, c, self.debug)
        self.if_stack.append(ifstmt)
        self.dbg_msg("parsing IF-body")
        body = self.stmtlist()
        prev_body = body;
        ifstmt.set_body( body )
        ptok = self.peek()
        while ( ptok.kind == EzhilToken.ATRATEOF or ptok.kind == EzhilToken.ELSE ):
            self.inside_if = True        
            [l,c]=ptok.get_line_col()
            if ( ptok.kind == EzhilToken.ATRATEOF ):
                # parse elseif branch
                self.dbg_msg("parsing ELSE-IF")                
                self.match( EzhilToken.ATRATEOF )
                exp = self.valuelist();
                self.dbg_msg("parsing ELSE-IF EXPR")
                tok = self.peek()
                if ( tok.kind != EzhilToken.ELSEIF ):
                    # maybe another IF statement, SWITCH-CASE or a WHILE loop, DO-WHILE loop etc.
                    next_stmt = self.stmtlist(exp) #pass in the expression                                        
                    prev_body.append( next_stmt )
                    # append to previously scanned body.
                else:
                    self.dbg_msg("parsing ELSE-IF-body")
                    self.match( EzhilToken.ELSEIF )
                    body = self.stmtlist()
                    prev_body = body
                    next_stmt = IfStmt(exp[0],body,None,l,c,self.debug)                    
                    ifstmt.append_stmt( next_stmt )
            elif ( ptok.kind == EzhilToken.ELSE ):
                #parse else branch                
                self.dbg_msg("parsing stmt else: ")
                self.match( EzhilToken.ELSE )
                self.dbg_msg("parsing ELSE-Body")
                self.inside_if = False
                body = self.stmtlist()
                prev_body = body;
                else_stmt = ElseStmt( body , l, c, self.debug)                
                ifstmt.append_stmt( else_stmt )
                break
            else:
                self.inside_if = False
                raise ParseException("If-Else-If statement syntax is messed up")
            ptok = self.peek()
            self.dbg_msg("parsing -IF next bits "+str(ptok))
        self.match( EzhilToken.END )
        self.inside_if = False
        self.dbg_msg("parsing -IF-complete")
        return ifstmt
    
    def stmt(self,pass_in_ATexpr=None):
        """ try an assign, print, return, if or eval statement """
        self.dbg_msg(" STMT ")
        ptok = self.peek()
        self.dbg_msg("stmt: peeking at "+str(ptok))
        if ( ptok.kind ==  EzhilToken.RETURN ):
            ## return <expression>
            self.dbg_msg('enter->return: <expression>')
            ret_tok = self.dequeue()
            [l,c]=ret_tok.get_line_col();
            if ( not self.parsing_function ):
                raise ParseException( "return statement outside of function body "+str(ret_tok))
            rstmt = ReturnStmt(self.expr(),l,c,self.debug)
            self.dbg_msg("return statement parsed")
            return rstmt
        elif ( ptok.kind ==  EzhilToken.PRINT ):
            self.currently_parsing.append( ptok )
            ## print <expression>
            print_tok = self.dequeue()
            [l,c]=print_tok.get_line_col();
            exprlist_val = self.exprlist();
            self.currently_parsing.pop()
            return PrintStmt(exprlist_val,l,c,self.debug)        
        elif ( ptok.kind ==  EzhilToken.ATRATEOF or pass_in_ATexpr):
            ## @ <expression> {if | while | elseif}
            if not pass_in_ATexpr:
                at_tok = self.match(EzhilToken.ATRATEOF)
                self.currently_parsing.append( at_tok )
                exp = self.valuelist();
                self.currently_parsing.pop()
            else:
                exp = pass_in_ATexpr
                pass_in_ATexpr = None #use it just once
            if( self.debug ): print ("return from valuelist ",str(exp))
            ptok = self.peek();
            if ( ptok.kind == EzhilToken.IF ):                
                return self.parseIfStmt(exp)
            elif ( ptok.kind ==  EzhilToken.WHILE ):
                ## @ ( expr ) while { body } end               
               self.loop_stack.append(True)
               self.dbg_msg("while-statement")
               while_tok = self.dequeue()
               self.currently_parsing.append( while_tok )
               [l,c]=while_tok.get_line_col()
               wexpr = exp[0];
               body = self.stmtlist( )
               self.match( EzhilToken.END)
               whilestmt = WhileStmt(wexpr, body, l, c, self.debug)
               self.loop_stack.pop()
               self.currently_parsing.pop()
               return whilestmt
            elif ( ptok.kind ==  EzhilToken.SWITCH ):
                return self.parseSwitchStmt(exp)
            elif ( ptok.kind ==  EzhilToken.FOREACH ):
                foreach_tok = self.dequeue()
                self.currently_parsing.append(foreach_tok)
                [l,c]=foreach_tok.get_line_col()
                if ( self.debug ): print("parsing FOREACH stmt")
                self.loop_stack.append(True)
                self.dbg_msg("foreach-statement")
                # convert to a for statement - building Ezhil AST - transformations
                if not isinstance( exp[1], Identifier ):
                    raise ParseException(" FOR-EACH statement "+str(foreach_tok) )
                foreach_iter = exp[1];
                iter = Identifier("__"+foreach_iter.id,l=0,c=-1);
                eq_token = EzhilLexeme("=",EzhilToken.EQUALS)
                plus_token = EzhilLexeme("+",EzhilToken.PLUS)
                lt_token = EzhilLexeme("<",EzhilToken.LT)
                if ( self.debug ): print("build init assign stmt")
                init = AssignStmt( iter, eq_token , Number(0),l,c,self.debug)
                if ( self.debug ): print("build cond expr")
                VL1 = ValueList([exp[0]],l,c,self.debug)
                cond = Expr( iter, lt_token, ExprCall( Identifier("len",l,c), VL1, l, c, self.debug ), l, c, self.debug )
                if ( self.debug ): print("build plus1 stmt")
                plus1_iter = Expr( iter, plus_token, Number(1), l, c, self.debug  )
                if ( self.debug ): print("build equals stmt")
                update = AssignStmt( iter, eq_token , plus1_iter ,l,c,self.debug)
                body = self.stmtlist() #parse body
                # and insert artifical update variable in body
                VL2 = ValueList([exp[0],iter],l,c,self.debug)
                extract_foreach_iter_from_list = ExprCall( Identifier("__getitem__",l,c), VL2,l,c,self.debug);
                foreach_iter_Assign = AssignStmt( foreach_iter, eq_token , extract_foreach_iter_from_list, l,c,self.debug )
                body.List.insert( 0,foreach_iter_Assign)
                # complete FOREACH stmt
                self.match( EzhilToken.END)
                self.currently_parsing.pop()
                foreach_stmt = ForStmt(init, cond, update, body, l, c, self.debug);                
                self.loop_stack.pop();                
                if ( self.debug ): print("completed parsing FOR-EACH loop",str(foreach_stmt))
                return foreach_stmt
            elif ( ptok.kind ==  EzhilToken.FOR ):
                ## Fixme : empty for loops not allowed.
                """ For ( exp1 , exp2 , exp3 ) stmtlist  end"""
                if ( self.debug ): print("parsing FOR stmt")
                self.loop_stack.append(True)
                self.dbg_msg("for-statement")                
                for_tok = self.peek()
                self.currently_parsing.append(for_tok)
                if ( self.debug ): print("matching for STMT",str(self.peek()))
                self.match( EzhilToken.FOR )
                if ( self.debug ): print("matched for STMT",str(self.peek()))
                [l,c]= for_tok.get_line_col();
                init,cond,update = exp[0],exp[1],exp[2]            
                if ( self.debug ): print("extract 3 parts",str(init),str(cond),str(update))
                body = self.stmtlist()
                self.match( EzhilToken.END)
                self.currently_parsing.pop()
                if ( self.debug ): print("body of loop",str(body))
                forstmt = ForStmt(init, cond, update, body, l, c, self.debug);
                self.loop_stack.pop();
                if ( self.debug ): print("completed parsing FOR loop",str(forstmt))
                return forstmt
        elif ( ptok.kind == EzhilToken.DO ):
            if ( self.debug ): print("parsing DO-WHILE statement")
            self.loop_stack.append(True)
            do_tok = self.dequeue()
            self.currently_parsing.append(do_tok)
            [l,c]=do_tok.get_line_col()
            body = self.stmtlist()
            if ( self.debug ): print("parsed body")
            self.match(EzhilToken.DOWHILE)            
            self.match(EzhilToken.ATRATEOF)
            exp = self.valuelist();
            if ( self.debug ): print("parsed EXP",exp[0])
            doWhileStmt = DoWhileStmt(exp[0], body, l, c, self.debug)
            self.loop_stack.pop()
            self.currently_parsing.pop()
            return doWhileStmt
        elif ( ptok.kind ==  EzhilToken.BREAK ):
            ## break, must be in loop-environment
            self.dbg_msg("break-statement");
            break_tok = self.dequeue();
            [l,c]=break_tok.get_line_col()
            self.check_loop_stack(); ##raises a parse error
            brkstmt = BreakStmt( l, c, self.debug);
            return brkstmt
        elif ( ptok.kind ==  EzhilToken.CONTINUE ):
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
            self.currently_parsing.append(ptok)
            [l,c] = ptok.get_line_col()
            lhs = self.expr()
            self.dbg_msg("parsing expr: "+str(lhs))
            ptok = self.peek()
            if ( ptok.kind in  EzhilToken.ASSIGNOP ):
                assign_tok = self.dequeue()
                rhs = self.expr()
                [l,c]=assign_tok.get_line_col()
                self.currently_parsing.pop()
                return AssignStmt( lhs, assign_tok, rhs, l, c, self.debug)
            self.currently_parsing.pop()
            return EvalStmt( lhs, l, c, self.debug )
        raise ParseException("parsing Statement, unknown operators" + str(ptok))
    
    def function(self):
        """ def[kw] fname[id] (arglist) {body} end[kw] """
        if ( self.parsing_function ):
            self.parsing_function = False
            raise ParseException(" Nested functions not allowed! "+str(self.last_token()))

        self.parsing_function = True
        def_tok = self.dequeue()
        if ( def_tok.kind !=  EzhilToken.DEF ):
            raise ParseException("unmatched 'def'  in function " +str(def_tok))
        
        id_tok = self.dequeue()
        if ( id_tok.kind !=  EzhilToken.ID ):
            raise ParseException("expected identifier in function"+str(id_tok))
        
        arglist = self.arglist()
        self.dbg_msg( "finished parsing arglist" )
        body = self.stmtlist()

        self.match(  EzhilToken.END )
        [l,c] = def_tok.get_line_col()
        fval = Function( id_tok.val, arglist, body, l, c, self.debug )
        self.parsing_function = False
        self.dbg_msg( "finished parsing function" ) 
        return fval

    def valuelist(self):
        """parse: ( expr_1 , expr_2, ... ) """
        valueList = list()
        self.dbg_msg("valuelist: ")
        lparen_tok = self.match(  EzhilToken.LPAREN )
        while ( self.peek().kind !=  EzhilToken.RPAREN ):            
            val = self.expr()
            if ( self.debug ): print("val = ",str(val))
            ptok = self.peek()
            if ( self.debug ) : print("ptok = ",str(ptok),str(ptok.kind),str(EzhilToken.ASSIGNOP))
            if ( ptok.kind in  EzhilToken.ASSIGNOP ):
                assign_tok = self.dequeue()
                rhs = self.expr()
                [l,c]=assign_tok.get_line_col()
                lhs = val
                val =  AssignStmt( lhs, assign_tok, rhs, l, c, self.debug)
                if ( self.debug ): print("AssignStmt = ",str(val))
                ptok = self.peek()
            else:
                if ( self.debug ): print("No-Assign // Expr =",str(val))
            self.dbg_msg("valuelist-expr: "+str(val))
            valueList.append( val )
            if  ( ptok.kind ==  EzhilToken.RPAREN ):
                break
            elif ( ptok.kind ==  EzhilToken.COMMA ):
                self.match(  EzhilToken.COMMA )
            else:
                raise ParseException(" function call argument list "+str(ptok))
        self.match(  EzhilToken.RPAREN )
        [l,c] = lparen_tok.get_line_col()
        return ValueList(valueList, l, c, self.debug )

    def arglist(self):
        """parse: ( arg_1, arg_2, ... ) """
        self.dbg_msg( " ARGLIST " )
        args = list()
        lparen_tok = self.match(  EzhilToken.LPAREN )
        while ( self.peek().kind !=  EzhilToken.RPAREN ):
            arg_name = self.dequeue()
            args.append( arg_name.val )
            ptok = self.peek()
            if  ( ptok.kind ==  EzhilToken.RPAREN ):
                break
            elif ( ptok.kind ==  EzhilToken.COMMA ):
                self.match(  EzhilToken.COMMA )
            else:
                raise ParseException(" function definition argument list "
                                     +str(ptok))
        self.match(  EzhilToken.RPAREN )
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
            if self.lex.peek().kind !=  EzhilToken.COMMA:
                break            
            tok = self.match( EzhilToken.COMMA)
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
        if ptok.kind in  EzhilToken.ADDSUB:
            binop=self.dequeue()
            if ( ptok.kind == EzhilToken.MINUS ):
                val2 = self.term()
            else:
                val2=self.expr()
            [l,c] = binop.get_line_col()
            res=Expr(val1,binop,val2, l, c, self.debug )
        elif ptok.kind ==  EzhilToken.LPAREN:
            ## function call
            if ( res.__class__ != Identifier ):
                raise ParseException("invalid function call"+str(ptok))
            [l,c] = ptok.get_line_col()
            vallist = self.valuelist()
            res=ExprCall( res, vallist, l, c, self.debug )
        
        ptok = self.peek()
        while  ptok.kind in EzhilToken.BINOP:
            binop = self.dequeue()
            [l,c] = binop.get_line_col()
            res = Expr( res, binop,self.expr(), l,c,self.debug)
            ptok = self.peek()
        return res
    
    def term(self):
        """ this is a grammar abstraction; 
        but AST only has Expr elements"""
        self.dbg_msg( "term" )
        val1=self.factor()
        res=val1

        tok = self.peek()
        if ( tok.kind in  EzhilToken.MULDIV 
             or  tok.kind in  EzhilToken.COMPARE 
             or tok.kind in  EzhilToken.EXPMOD 
             or tok.kind in EzhilToken.BITWISE_AND_LOGICAL ):
            binop=self.dequeue()
            val2=self.term()
            [l,c] = binop.get_line_col()
            res=Expr(val1,binop,val2, l, c, self.debug)
            
        return res
    
    def factor(self):
        self.dbg_msg( "factor" )
        tok=self.peek()
        if tok.kind ==  EzhilToken.LPAREN:
            lparen_tok = self.dequeue()
            val=self.expr()
            if self.dequeue().kind!= EzhilToken.RPAREN:
                raise SyntaxError("Missing Parens "+str(self.last_token()))
        elif tok.kind ==  EzhilToken.NUMBER:
            tok_num = self.dequeue()
            [l, c] = tok_num.get_line_col()
            val = Number( tok.val , l, c, self.debug )
        elif tok.kind == EzhilToken.LOGICAL_NOT:
            tok_not = self.dequeue()
            [l, c] = tok_not.get_line_col()
            val = UnaryExpr( self.expr(), tok_not , l, c, self.debug )
            self.dbg_msg("completed parsing unary expression"+str(val))
        elif tok.kind ==  EzhilToken.ID:
            tok_id = self.dequeue()
            [l, c] = tok_id.get_line_col()
            val = Identifier( tok.val , l, c, self.debug )
            ptok = self.peek()
            self.dbg_msg("factor: "+str(ptok) + " / "+str(tok) )
            if ( ptok.kind ==  EzhilToken.LPAREN ):
                ## function call
                [l, c] = ptok.get_line_col()
                vallist = self.valuelist()
                val=ExprCall( val, vallist, l, c, self.debug )
            elif ( ptok.kind ==  EzhilToken.LSQRBRACE ):
                ## indexing a array type variable or ID
                val=None
                raise ParseException("arrays not implemented"+str(ptok));
        elif tok.kind ==  EzhilToken.STRING :
            str_tok = self.dequeue()
            [l,c] = str_tok.get_line_col()
            val = String( tok.val , l, c, self.debug )
        elif tok.kind in EzhilToken.ADDSUB:
            unop = self.dequeue();
            [l, c] = unop.get_line_col()
            val=Expr(Number(0),unop,self.term(),l,c,self.debug);
        elif tok.kind == EzhilToken.LSQRBRACE:
            # creating a list/array expression
            list_start = self.dequeue();
            val = Array()
            while( True ):
                if ( self.peek().kind == EzhilToken.RSQRBRACE ):
                    break;
                exprval = self.expr()
                val.append( exprval  )
                if self.debug : print(self.peek().__class__,self.peek())
                if ( self.peek().kind == EzhilToken.RSQRBRACE ):
                    break
                else:
                    assert( self.peek().kind == EzhilToken.COMMA)
                    self.dequeue()
            assert( self.peek().kind == EzhilToken.RSQRBRACE )
            list_end = self.dequeue()
        else:
            raise ParseException("Expected Number, found something "+str(tok))
        
        self.dbg_msg( "factor-returning: "+str(val) )
        return val
