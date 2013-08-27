#!/usr/bin/python
# -*- coding: utf-8 -*-
## 
## (C) 2007, 2008 Muthiah Annamalai,
## Licensed under GPL Version 3
## 
## Module has elements of PARSE-TREE  AST 
## in the classes Expr, ExprCall, ExprList, Stmt, ReturnStmt,
## BreakStmt, ContinueStmt, ElseStmt, IfStmt, WhileStmt, 
## ForStmt, AssignStmt, PrintStmt, EvalStmt, ArgList,
## ValueList, Function, StmtList, Identifier, String, Number,
## Array, Hash

import copy
import math
## scanner for exprs language
from scanner import Token, Lexeme, Lex

## runtime elements
from runtime import  Environment, BuiltinFunction, \
 BlindBuiltins

## exceptions
from errors import RuntimeException, ParseException

##
## ATOMS
##

class Identifier:
    def __init__(self,id, l, c, dbg=False):
        self.id=id
        self.debug = dbg
        self.line = l;
        self.col = c;

    def dbg_msg(self, msg):
        """ handy to print debug messages """
        if ( self.debug ):
            print("## "+msg)
        return

    def __repr__(self):
        return "\n\t [Identifier [" + str(self.id) +"]]"

    def evaluate(self,env):
        if ( env.has_id(self.id)):
            val = env.get_id(self.id)
            if ( hasattr( val, 'evaluate' ) ):
                val = val.evaluate(env)
            elif ( val.__class__ == str ):
                #val = val
                pass
            else:
                #val = val
                pass
            self.dbg_msg( str(self) + " = val ["+str(val) + "]" )
            return val
        raise RuntimeException("Cannot Find Identifier %s at \
 Line %d, col %d"%( self.id, self.line,self.col ) )
        return None

    def visit(self, walker):
        """ visitor - do something with a identifier """
        walker.visit_identifier(self)
        return

class String:
    def __init__(self,s, l = 0, c = -1, dbg = False):
        self.string = s
        self.debug = dbg
        self.line = l
        self.col = c
    
    def __repr__(self):
        return " [String [" + str(self.string) +"]] "
    
    def __str__(self):
        return self.string

    def evaluate(self,env):
        return self.string

    def visit(self, walker):
        walker.visit_string(self)
        return

class Number:
    def __init__(self,n, l = 0, c = -1, dbg = False):
        self.num=n
        self.debug = dbg
        self.line = l
        self.col = c

    def __int__(self):
        return int(self.num)

    def __float__(self):
        return float(self.num)
    
    def __repr__(self):
        return " [Number [" + str(self.num) +"]]"
    
    def __str__(self):
        return self.num.__str__()

    def evaluate(self,env):
        return self.num

    def visit(self, walker):
        walker.visit_number(self)
        return

class Boolean(Number):
    def __init__(self,n, l = 0, c = -1, dbg = False):
        Number.__init__(self,n,l,c,dbg)
    def __str__(self):
        if ( self.num ):
            return "True"
        return "False"

class Dict(dict):
    def __init__(self):
        dict.__init__(self)

    def base_evaluate(self,env):
        rval = {}
        for x,y in self.items():
            rval.update({ x.evaluate( env ): y.evaluate( env )} )
        return rval
    
    def evaluate(self,env):
        """ how do you evaluate dictionaries? just return the favor """
        return self.base_evaluate( env )

## FIXME: implement arrays
class Array(list):
    def __init__(self):
        pass

    def base_evaluate(self,env):
        rval = []
        for v in self:
            rval.append( v.evaluate(env) )
        return rval

    def evaluate(self,env):
        return self.base_evaluate( env )

class Hash(dict):
    pass

class ExprCall:
    """handle function call statement etc."""
    def __init__(self,func_id,arglist, l, c, dbg = False):
        self.func_id = func_id 
        self.fname = func_id.id
        self.arglist = arglist
        self.debug = dbg
        self.line = l
        self.col = c

    def dbg_msg(self, msg):
        if ( self.debug ):
            print("## ",msg)
        return

    def __repr__(self):
        return "\n\t [ExprCall[ "+str(self.fname)+" (" \
            +str(self.arglist)+")]]"
    
    def evaluate(self,env):
        self.dbg_msg( str(env) )
        if ( env.has_function(self.fname) ):
            self.dbg_msg("calling function "+ self.fname)
            fval = env.get_function(self.fname)
            ## use applicative order evaluation.
            eval_arglist = [ i.evaluate(env) for i in self.arglist.get_list()];
            env.set_args(  eval_arglist )
            rval = fval.evaluate(env)
            self.dbg_msg( "function retval ="+str(rval)+str(type(rval)))
        else:
            raise RuntimeException("undefined function: %s near ( %d, %d )"%(self.fname, self.line, self.col) )
        return rval

    def visit(self,walker):
        walker.visit_expr_call(self)
        return
    
class ExprList:
    def __init__(self,exprs, l, c, dbg=False):
        self.exprs = exprs
        self.debug = dbg
        self.line = l
        self.col = c

    def __repr__(self):
        return "\n\t [ExprList[ "+ ", ".join(map(str,self.exprs)) + "]]"

    def evaluate(self,env):
        """evaluate  a, b, c ... z to a string"""
        z = []
        for exp_itr in self.exprs:
            z.append(exp_itr.evaluate(env))
        return ", ".join(map(str,z))
    
    def visit(self, walker):
        walker.visit_expr_list(self)
        return    

class Stmt:
    def __init__(self, l=0, c=0, dbg =False):
        """ implements an empty statement"""
        self.line = l
        self.col = c
        self.class_name = "Stmt"
        self.debug = dbg
    
    def dbg_msg(self, msg):
        """ handy to print debug messages """
        if ( self.debug ):
            print(msg)
        return
        
    def __repr__(self):
        return "\n\t [%s[empty-statement]] "%(self.class_name)

    def get_pos(self):
        return "line %d, col %d"%(self.line,self.col)
        
    def evaluate(self, env):
        """ empty statement """
        return None

    def is_true_value(self, val):
        """ Decide if the val is agreeable to True.
        Right now keep it simple however."""
        rval = False
        self.dbg_msg("is_true_value? "+ str(val.__class__))
        try:
            #print val, type(val)
            #if hasattr(val,'num'):
            #    fval = val.num
            if ( hasattr(val,'evaluate') ):
                fval = val.evaluate(None);
            elif ( isinstance(val,float) or isinstance(val,int) ):
                fval = val
            else:
                raise  Exception("Unknown case, cannot identify truth @ "+self.get_pos()+" for value "+str(val))
            
            if ( fval > 0.0 ):
                rval = True
            ## all other cases later.
        except Exception as pyEx:
            """ objects where is_true_value() is not supported """
            print(pyEx)
            raise RuntimeException(pyEx)
        self.dbg_msg('Is True Value? ' + str(rval) + str(val.__class__) )
        return rval
    
    def visit( self, walker):
        walker.visit_stmt( self )
        return
    
class UnaryExpr(Stmt):
    def __init__(self,t,op,l,c,dbg=False):
        Stmt.__init__(self,l,c,dbg)
        self.term=t
        self.unaryop=op

    def do_unaryop(self,tval):
        if ( self.unaryop.kind == Token.LOGICAL_NOT ):
            if not tval:
                return Boolean( True )
            else:
                return Boolean( False )
        else:
            raise RuntimeException(" unknown Unary Operation - "+str(self.unaryop)+" not supported")
        return

    def evaluate(self,env):
        term=self.term.evaluate(env)
        if ( self.debug ): print(term, type(term))
        if self.unaryop.kind in Token.UNARYOP:
            tval = Expr.normalize_values( self, term, env)
            if ( self.debug ): print(tval, type(tval))
            term = self.do_unaryop( tval )
        else:
            raise RuntimeException(" unknown Unary Operation - "+str(self.unaryop)+" not supported")
        if ( self.debug ): print("term = ",term, term.__class__)
        return term

class Expr(Stmt):
    One = Number ( 1 );
    Zero = Number ( 0 );
    def __init__(self,t,op,next_expr,l,c,dbg=False):
        Stmt.__init__(self,l,c,dbg)
        self.term=t
        self.binop=op
        self.next_expr=next_expr        

    def __repr__(self):
        return "\n\t [Expr[ "+ str(self.term)+"] " + \
               Token.token_types[self.binop.kind] + \
               "\t NextExpr [" + str(self.next_expr) + "]]"

    def do_binop(self,opr1,opr2, binop):
        self.dbg_msg(" Doing binary operator " + Token.token_types[binop])
        if binop == Token.PLUS:
            self.dbg_msg("addition")
            val = Number(opr1+opr2)
        elif binop == Token.MINUS:
            self.dbg_msg("subtraction")
            val = Number(opr1-opr2)
        elif binop == Token.PROD:
            self.dbg_msg("multiplication")
            val = Number(opr1*opr2)
        elif binop == Token.DIV:
            self.dbg_msg("division")
            val = Number(opr1/opr2)
        elif binop == Token.MOD:
            self.dbg_msg("modulo")
            val = Number(math.fmod(opr1,opr2));
        elif binop == Token.EXP:
            self.dbg_msg("exponent")
            val = Number(math.pow(opr1,opr2));
        elif binop == Token.GT:
            self.dbg_msg("GT > ")
            val = self.Zero;
            if ( opr1 > opr2 ):
                val = self.One;
        elif binop == Token.GTEQ:
            self.dbg_msg("GTEQ >= ")
            val =  self.Zero;
            if ( opr1 >= opr2 ):
                val = self.One;
        elif binop == Token.LT:
            self.dbg_msg("LT < ")
            val =  self.Zero;
            if ( opr1 < opr2 ):
                val = self.One;
        elif binop == Token.LTEQ:
            self.dbg_msg("LT <= ")
            val =  self.Zero;
            if ( opr1 <= opr2 ):
                val = self.One;
        elif binop == Token.NEQ:
            self.dbg_msg("NEQ != ")
            val =  self.Zero;
            if ( opr1 != opr2 ):
                val = self.One;
        elif binop == Token.EQUALITY:
            ## FIXME: do many equality tests than just value
            ## based tests.
            self.dbg_msg("EQUALITY ==  ")
            val =  self.Zero;
            if ( opr1 == opr2 ):
                val = self.One;
        elif binop == Token.LOGICAL_AND:
            self.dbg_msg("LOGICAL AND")
            val = self.Zero
            if ( opr1 and opr2 ):
                val = self.One;
        elif binop == Token.LOGICAL_OR:
            self.dbg_msg("LOGICAL OR")
            val = self.Zero
            if ( opr1 or opr2 ):
                val = self.One;
        elif binop in [Token.BITWISE_AND, Token.BITWISE_OR]:
            raise Exception("Ezhil : Bitwise operators AND '&' and OR '|' are not supported currently!")
        else:
            raise SyntaxError("Binary operator syntax not OK @ "+self.get_pos())
        self.dbg_msg("value = "+str(val))
        return val

    @staticmethod
    def normalize_values( obj, term, env ):
        if ( hasattr(term,'evaluate') ):
            if ( isinstance(term,Number) ): #work for both Number, and derived Boolean class
                tval = term.num
            elif ( isinstance(term,String) ):
                tval = term.string                            
            else:
                ## print term.__class__,term,str(term)
                ## possibly leads to inf- recursion
                ## tval = term.evaluate( env )
                raise RuntimeException( " cannot normalize token; unknown clause,"+str(term)+", to evaluate @ "+obj.get_pos());
        else:
            tval = (term) #float cast not required.
        return tval
    
    def evaluate(self,env):
        term=self.term.evaluate(env)
        if ( self.debug ): print term, type(term)
        if self.binop.kind in Token.BINOP:
            tnext = self.next_expr.evaluate(env)
            tval = Expr.normalize_values( self, term, env)
            tval2 = Expr.normalize_values( self, tnext, env)
            if ( self.debug ): print tval, type(tval), tval2, type(tval2)
            try:
                term = self.do_binop(tval,
                                     tval2,
                                     self.binop.kind)
            except Exception as binOp_Except:
                raise RuntimeException("binary operation "+str(self.term)+str(self.binop)+str(self.next_expr)+" failed with exception "+str(binOp_Except))
        else:
            raise RuntimeException(" unknown Binary Operation - Binary operation "+str(self.binop)+" not supported")
        if ( self.debug ): print "term = ",term, term.__class__
        return term

    def visit(self, walker):
        walker.visit_expr(self)
        return

class ReturnStmt(Stmt):
    """ return expr """
    def __init__(self,rval,l,c,dbg=False):
        Stmt.__init__(self,l,c,dbg)
        self.rvalue=rval
        
    def __repr__(self):
        return "\n\t [ReturnStmt[ "+ str(self.rvalue)+"]]\n"

    def evaluate(self,env):
        rhs=self.rvalue.evaluate(env)
        self.dbg_msg("return statement evaluated to "+str(rhs))
        env.set_retval(rhs)
        return rhs
    
    def visit(self, walker):
        walker.visit_return_stmt(self)
        return

class BreakStmt(Stmt):
    """ return expr """
    def __init__(self,l,c,dbg=False):
        Stmt.__init__(self,l,c,dbg)

    def __repr__(self):
        return "\n\t [BreakStmt]\n"

    def evaluate(self,env):
        self.dbg_msg("break statement")
        env.set_break()
        return None
    
    def visit(self, walker):
        walker.visit_break_stmt(self)
        return

class ContinueStmt(Stmt):
    """ return expr """
    def __init__(self,l,c,dbg=False):
        Stmt.__init__(self,l,c,dbg)
    
    def __repr__(self):
        return "\n\t [ContinueStmt]\n"

    def evaluate(self,env):
        self.dbg_msg("continue statement")
        env.set_continue()
        return None
    
    def visit(self, walker):
        walker.visit_continue_stmt(self)
        return

class ElseStmt(Stmt):
    def __init__(self,stmt,l,c, dbg):
        Stmt.__init__(self,l,c,dbg)
        self.stmt = stmt
        self.class_name = "ElseStmt"

    def __repr__(self):
        return "\t [ElseStmt ["+str(self.stmt)+"]]\n"
    
    def evaluate(self,env):
        return self.stmt.evaluate(env)
    
    def visit(self,walker):
        walker.visit_else_stmt(self)
        return

class IfStmt(Stmt):
    """ if ( op ) stmtlist {else | elseif ( op )| stmt } end"""
    def __init__(self,expr,body,next_stmt,l,c,dbg=False):
        Stmt.__init__(self,l,c,dbg)
        self.expr = expr
        self.body = body
        self.class_name = "IfStmt"
        ## this is either another IfStmt or an Else Stmt.
        if not next_stmt:
            self.next_stmt = []
        else:
            self.next_stmt = next_stmt
        
    def __repr__(self):
        rval = "\t\n [IfStmt[["+str(self.expr)+ "]] "+str(self.body)
        if ( self.next_stmt ):
            rval = rval + str(self.next_stmt)
        rval = rval + "]"
        return rval

    def set_body(self,body):
        self.body = body
    
    def append_stmt(self,stmt):
        self.next_stmt.append(stmt)
        return
        
    def set_next_stmt(self, stmt):
        self.next_stmt = stmt
    
    def evaluate(self,env):
        self.dbg_msg( "Eval-if-stmt" + str(self.expr) )
        rval = None
        self.dbg_msg("eval-if stmt")
        if ( self.is_true_value ( self.expr.evaluate(env) ) ):
            self.dbg_msg("ifstmt: true condition")
            rval = self.body.evaluate( env )
            return rval
        self.dbg_msg("ifstmt: false condition")
        for elseif_or_else in self.next_stmt:
            if ( isinstance( elseif_or_else, IfStmt ) ):
                if ( self.is_true_value( elseif_or_else.expr.evaluate(env) ) ):
                    rval = elseif_or_else.body.evaluate( env )
                    return rval
                else:
                    # elseif branch was found to be false. Continue
                    continue;
            elif( isinstance( elseif_or_else, ElseStmt ) ):
                rval = elseif_or_else.evaluate( env )
                return rval
            else:
                raise RuntimeException("IF-ELSEIF-ELSE was parsed wrongly, unknown construct found")
        # its perfectly legal to not have an else statement
        return rval 
    
    def visit(self,walker):
        walker.visit_if_elseif_stmt(self)
        return

class WhileStmt(Stmt):
    """ while ( exp ) stmtlist  end"""
    def __init__(self,expr,body,l,c,dbg=False):
        Stmt.__init__(self,l,c,dbg)
        self.expr = expr
        self.body = body
        self.class_name = "WhileStmt"

    def __repr__(self):
        rval = "\t\n [%s[["%str(self.__class__)+str(self.expr)+ "]] "+str(self.body) +"]"
        return rval

    def evaluate(self,env):
        rval = None
        self.dbg_msg("eval-While stmt")
        while ( self.is_true_value ( self.expr.evaluate(env) ) 
                and not env.get_break_return() ):
            ## everytime of loop clear any continues
            env.clear_continue()
            self.dbg_msg("ifstmt: true condition")
            rval = self.body.evaluate( env )
        ## clear break if-any
        env.clear_break();
        self.dbg_msg("exiting While-stmt with rval="+str(rval))
        return rval

    def visit(self,walker):
        walker.visit_while_stmt(self)
        return

class DoWhileStmt(WhileStmt):
    """ do stmtlist  while ( exp )"""
    def __init__(self,expr,body,l,c,dbg=False):
        WhileStmt.__init__(self,expr,body,l,c,dbg)
        
    def evaluate(self,env):
        """ first run is on the house, but then we keep count. Dog bites American style """
        rval = None
        first_time = True
        self.dbg_msg("eval-Do-While stmt")
        while ( first_time or self.is_true_value ( self.expr.evaluate(env) ) 
                and not env.get_break_return() ):
            ## everytime of loop clear any continues
            env.clear_continue()
            self.dbg_msg("ifstmt: true condition")
            rval = self.body.evaluate( env )
            first_time = False
        ## clear break if-any
        env.clear_break();
        self.dbg_msg("exiting Do-While-stmt with rval="+str(rval))
        return rval

class ForStmt(Stmt):
    """ For ( exp1 ; exp2 ; exp3 ) stmtlist  end"""
    def __init__(self,expr1,expr2, expr3,body,l,c,dbg=False):
        Stmt.__init__(self,l,c,dbg)
        self.expr_init = expr1;
        self.expr_cond = expr2;
        self.expr_update = expr3;        
        self.body = body
        self.class_name = "ForStmt"
    
    def __repr__(self):
        rval = "\t\n [ForStmt[[ ("+str(self.expr_init)+"; "+\
            str(self.expr_cond) + "; " +\
            str(self.expr_update)+") ]] " + str(self.body) +"]"
        return rval

    def evaluate(self,env):
        self.dbg_msg( "Eval-For-stmt: ")
        rval = None
        self.dbg_msg("eval-For-stmt")
        rval = self.expr_init.evaluate(env)        
        while ( self.is_true_value ( self.expr_cond.evaluate(env) )
                and not env.get_break_return() ):
            ## everytime of loop clear any continues
            env.clear_continue()
            rval = self.body.evaluate( env )
            # update happens after body evaluates - this is C-style            
            self.expr_update.evaluate( env )
        ## clear break if-any
        env.clear_break();
        self.dbg_msg("exiting For-stmt with rval="+str(rval))
        return rval

    def visit(self,walker):
        walker.visit_for_stmt(self)
        return

class AssignStmt(Stmt):
    """ lhs = rhs """
    def __init__(self,lvalue,op,rvalue,l,c,dbg=False):
        Stmt.__init__(self,l,c,dbg)
        self.lvalue=lvalue
        self.assignop=op
        self.rvalue=rvalue
        self.class_name = "AssignStmt"

    def __repr__(self):
        return "\n\t [AssignStmt[ "+ str(self.lvalue)+"] " + \
               Token.token_types[self.assignop.kind] + \
               "\t Expr [" + str(self.rvalue) + "]]"

    def do_assignop(self, lvalue, rhs, kind, env):
        rval = None
        if ( kind == Token.EQUALS ):
            env.set_id( lvalue.id, rhs )
            rval = rhs
        else:
            raise Exception("Unknown assign operator @ "+self.get_pos())
        return rval
    
    def evaluate(self,env):
        if self.assignop.kind in Token.ASSIGNOP:
            self.dbg_msg("assignop: rhs = "+str(self.rvalue) )
            rhs = self.rvalue.evaluate(env)
            self.do_assignop(self.lvalue,
                             rhs,
                             self.assignop.kind, env)            
            self.dbg_msg("assignop lvalue ["+str(self.lvalue) \
                             +"] = ["+str(rhs) + \
                             "( saved as ) " + \
                             str(self.lvalue))
                             #str(env.get_id(self.lvalue.id)) )
            return rhs
        raise Exception("Unknown assign operator @ "+self.get_pos())
    
    def visit(self, walker):
        walker.visit_assign_stmt(self)
        return

class PrintStmt(Stmt):
    """ print EXPR """
    def __init__(self,exprlst, l, c, dbg):
        Stmt.__init__(self,l,c,dbg)
        self.exprlst = exprlst
        
    def __repr__(self):
        return "\n\t [PrintStmt[ "+ str(self.exprlst)+"]]"

    def do_printop(self,env):
        val = ""
        val = self.exprlst.evaluate( env  )
        if hasattr(val,'evaluate') :
            val = val.evaluate( env )
        print(val)
        return val
    
    def evaluate(self,env):
        self.do_printop(env)
        return None
    
    def visit(self, walker):
        walker.visit_print_stmt(self)
        return

class EvalStmt(Stmt):
    """ EXPR """
    def __init__(self,expr, l, c, dbg=False):
        Stmt.__init__(self,l,c,dbg)
        self.expr = expr
        
    def __repr__(self):
        #print type(self.expr)
        return "\n\t [EvalStmt[ "+ str(self.expr)+"/"+str((self.expr.__class__))+"]]"

    def evaluate(self,env):
        return self.expr.evaluate(env)

    def visit(self, walker):
        walker.visit_eval_stmt(self)
        return

## PLACEHOLDER
class ArgList:
    """ defines argument list in a function definition """
    def __init__(self,argvals, l, c, dbg=False):
        """ to get self.args, use get_list() method """
        self.args = argvals 
        self.line = l
        self.col = c

    def __len__(self):
        return len(self.args)

    def get_list(self):
        return self.args

    def __repr__(self):
        return "\n\t [ArgList["+ ",".join(map(str,self.args))+"]]"

    def visit(self,walker):
        walker.visit_arg_list(self)
        return

#TODO : derive from 'list' and 'Stmt' class and update code
class ValueList:
    """ defines value list in a function definition """
    def __init__(self,argvals, l, c, dbg =False):
        """ to get self.args, use get_list() method """
        self.args = argvals 
        self.debug = dbg
        self.line = l
        self.col = c

    def __len__(self):
        return len(self.args)
        
    def __getitem__(self,idx):
        """ index into the object like a list : @idx - caveat emptor """
        return self.args[idx]
    
    def get_list(self):
        return self.args

    #def evaluate(self):
    #    if ( isinstance(self.args,list) and len(self.args) == 1):
    #        return self.args[0]
    #    return self.args

    def __repr__(self):
        return "\n\t [ValueList["+ ",".join(map(str,self.args))+"]]"

    def visit(self,walker):
        walker.visit_value_list(self)
        return

    
class StmtList(Stmt):
    def __init__(self,stmt=[], dbg=False):
        Stmt.__init__(self,0,0,dbg)
        self.List = copy.copy(stmt)
        
    def __len__(self):
        return len(self.List)        
    
    def append(self,stmt_x):
        self.dbg_msg("adding new statement " + str(stmt_x) )
        self.List.append(stmt_x)
        return
    
    def __repr__(self):
        rval = "\t [StmtList[ "+ "\n ".join(map(str,self.List)) + "]]\n"
        return rval

    def evaluate(self,env):
        rval = None
        for stmt in self.List:
            self.dbg_msg( "STMTLIST => STMT" )
            if ( env.break_return_continue() ):
                break;
            rval = stmt.evaluate(env)
        return rval

    def visit(self,walker):
        """ visit stmt list method """
        walker.visit_stmt_list(self)
        return

class Function(Stmt):
    """ function definition itself """
    def __init__(self,fname,arglist,body,l,c,dbg=False):
        Stmt.__init__(self,l,c,dbg)
        self.name = fname
        self.arglist = arglist
        self.body = body
        self.dbg_msg( "function "+fname+" was defined" )
        
    def dbg_msg(self, msg):
        if ( self.debug ):
            print("## ",msg)
        return

    def __repr__(self):
        return "\n\t [Function[ "+ str(self.name)+"( " + \
            str(self.arglist) + ")]\n" + \
            "\t Body [" + str(self.body) + "]]\n"
    
    def evaluate(self,env):
        ## push stuff into the call-stack
        env.call_function(self.name)
        
        ## check arguments match, otherwise raise error
        args = env.get_args()#.get_list()
        fargs = self.arglist.get_list()
        if ( len(args) != len(fargs) ):
            raise Exception("Call Arguments donot match with" + \
                                "function definition @ "+self.get_pos())
        
        ## create local variables on the stack in order of definitions
        lut={}
        for idx in range(0,len(fargs)):
            varname = fargs[idx]
            value = args[idx]
            lut[varname]=value
        env.set_local(lut)
        
        ## invoke the function
        rval = self.body.evaluate(env)
        
        ## get the value from the stack.
        rval = env.get_retval( );

        env.clear_call()
        ## pop stuff into the call-stack
        env.return_function(self.name)
        return  rval

    def visit(self,walker):
        walker.visit_function(self)
        return

