#!/usr/bin/python
# -*- coding: utf-8 -*-
## 
## (C) 2007, 2008, 2013 Muthiah Annamalai,
## Licensed under GPL Version 3
## 
## Module has elements of PARSE-TREE  AST 
## in the classes Expr, ExprCall, ExprList, Stmt, ReturnStmt,
## BreakStmt, ContinueStmt, ElseStmt, IfStmt, WhileStmt, 
## ForStmt, AssignStmt, PrintStmt, EvalStmt, ArgList,
## ValueList, Function, StmtList, Identifier, String, Number,
## Array, Dict, NoOp

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

    def __unicode__(self):
        return u"" + self.id
    
    def dbg_msg(self, msg):
        """ handy to print debug messages """
        if ( self.debug ):
            print(u"## "+msg)
        return

    def __repr__(self):
        return u"\n\t [Identifier [" + unicode(self.id) +u"]]"

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
            self.dbg_msg( unicode(self) + " = val ["+unicode(val) + "]" )
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
        return u" [String [" + unicode(self.string) + u"]] "
    
    def __str__(self):
        return self.string

    def __unicode__(self):
        return unicode( self.string )

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
        return u" [Number [" + unicode(self.num) + u"]]"
    
    def __str__(self):
        return self.num.__str__()

    def __unicode__(self):
        return unicode( self.num )

    def evaluate(self,env):
        return self.num

    def visit(self, walker):
        walker.visit_number(self)
        return

class Boolean(Number):
    def __init__(self,n, l = 0, c = -1, dbg = False):
        Number.__init__(self,n,l,c,dbg)

    def __unicode(self):
        return self.__str__()

    def __str__(self):
        if ( self.num ):
            return u"True"
        return u"False"

class Dict(dict):
    def __init__(self):
        dict.__init__(self)
        
    def base_evaluate(self,env):
        rval = {}
        for x,y in self.items():
            rval.update({ x.evaluate( env ): y.evaluate( env )} )
        return rval
    
    def __unicode__(self):
        fmt = u"{"
        for k,v in self.items():
            fmt = fmt + unicode(k) + u" : " + unicode(v) + u",\n"
        fmt = fmt + u"}"
        return fmt
    
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
    
    def __unicode__(self):
        return u", ".join( [unicode(item) for item in self] )
    
    def evaluate(self,env):
        return self.base_evaluate( env )

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
        return u"\n\t [ExprCall[ "+unicode(self.fname)+u" (" \
            +unicode(self.arglist)+u")]]"
    
    def evaluate(self,env):
        self.dbg_msg( unicode(env) )
        if ( self.debug ):
            print(u"\n".join( env.builtin_map.keys() ))
            print("*"*60)
            print(u"\t".join(env.function_map.keys() ))
            print( self.fname, " ==?== ",env.builtin_map.get(self.fname,None))
        if ( env.has_function(self.fname) ):
            self.dbg_msg("calling function "+ self.fname)
            fval = env.get_function(self.fname)
            ## use applicative order evaluation.
            eval_arglist = [ i.evaluate(env) for i in self.arglist.get_list()];
            env.set_args(  eval_arglist )
            try:
                rval = fval.evaluate(env)
            except Exception as e:
                raise RuntimeException( str(e) )
            self.dbg_msg( u"function retval ="+unicode(rval)+unicode(type(rval)))
        else:
            raise RuntimeException(u"undefined function: ]%s[ near ( %d, %d )"%(self.fname, self.line, self.col) )
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
        return u"\n\t [ExprList[ "+ u", ".join(map(unicode,self.exprs)) + u"]]"

    def evaluate(self,env):
        """evaluate  a, b, c ... z to a string"""
        z = []
        for exp_itr in self.exprs:
            z.append(exp_itr.evaluate(env))
        return u", ".join(map(unicode,z))
    
    def visit(self, walker):
        walker.visit_expr_list(self)
        return    

class Stmt:
    def __init__(self, l=0, c=0, dbg =False):
        """ implements an empty statement"""
        self.line = l
        self.col = c
        self.class_name = u"Stmt"
        self.debug = dbg

    def __unicode__(self):        
        self.dbg_msg( u" ".join([ u"stmt => ", unicode(self.__class__)]) ) #we're headed toward assertion
        return self.__repr__()

    def __repr__(self):
        print("//#//"*50)
        print(u"stmt => ", unicode(self.__class__)) #we're headed toward assertion
        self.dbg_msg(u"stmt => "+ unicode(self.__class__) )
        raise Exception(u"FATAL : Class %s did not implement the __repr__ method, nor inherits a concrete implementation."%unicode(self.__class__))
    
    def dbg_msg(self, msg):
        """ handy to print debug messages """
        if ( self.debug ):
            print(msg)
        return
    
    def get_pos(self):
        return u"line %d, col %d"%(self.line,self.col)
        
    def evaluate(self, env):
        """ empty statement """
        return None

    def is_true_value(self, val):
        """ Decide if the val is agreeable to True.
        Right now keep it simple however."""
        rval = False
        self.dbg_msg(u"is_true_value? "+ unicode(val.__class__))
        try:
            if ( hasattr(val,'evaluate') ):
                fval = val.evaluate(None);
            elif ( isinstance(val,float) or isinstance(val,int) ):
                fval = val
            else:
                raise  Exception(u"Unknown case, cannot identify truth @ "+self.get_pos()+u" for value "+unicode(val))
            
            if ( fval > 0.0 ):
                rval = True
            ## all other cases later.
        except Exception as pyEx:
            """ objects where is_true_value() is not supported """
            print(pyEx)
            raise RuntimeException(pyEx)
        self.dbg_msg(u"Is True Value? " + unicode(rval) + unicode(val.__class__) )
        return rval
    
    def visit( self, walker):
        walker.visit_stmt( self )
        return

class DeclarationStmt(Stmt):
    """ hold function declaration statements; have visit option, 
        but no evaluation options. """
    def __init__(self,fcn):        
        if isinstance(fcn,Function):
            Stmt.__init__(self,fcn.line,fcn.col,fcn.debug)
            self.class_name = u"Declaration_Statement"
            self.fcn = fcn #FunctionStmt object
        else:
            raise Exception(u"declaration statement can only hold FunctionStmt objects")
    
    def visit( self, walker):
        """ delegate visitor to holding function """
        walker.visit_function( self.fcn )
        return
    
    def __repr__(self):        
        return self.fcn.__repr__()

class UnaryExpr(Stmt):
    def __init__(self,t,op,l,c,dbg=False):
        Stmt.__init__(self,l,c,dbg)
        self.term=t
        self.unaryop=op

    def __unicode__(self):
        return u"[UnaryExpr["+unicode(self.unaryop)+ ","+unicode(self.term)+"]]"
    
    def do_unaryop(self,tval):
        if ( self.unaryop.kind == Token.LOGICAL_NOT ):
            if not tval:
                return Boolean( True )
            else:
                return Boolean( False )
        else:
            raise RuntimeException(" unknown Unary Operation - "+unicode(self.unaryop)+" not supported")
        return

    def evaluate(self,env):
        term=self.term.evaluate(env)
        self.dbg_msg(u"unaryop=> "+unicode(term) +u" "+ unicode(term.__class__))
        if self.unaryop.kind in Token.UNARYOP:
            tval = Expr.normalize_values( self, term, env)
            if ( self.debug ): print(tval, type(tval))
            term = self.do_unaryop( tval )
        else:
            raise RuntimeException(" unknown Unary Operation - "+unicode(self.unaryop)+" not supported")        
        self.dbg_msg(u"unaryop=> "+u"term = "+unicode(term)+u" "+unicode(term.__class__))
        return term

class Expr(Stmt):
    One = Number ( 1 );
    Zero = Number ( 0 );
    def __init__(self,t,op,next_expr,l,c,dbg=False):
        Stmt.__init__(self,l,c,dbg)
        self.term=t
        self.binop=op
        self.next_expr=next_expr        

    def __len__(sef):
        """ expr is unit length always, as opposed to ExprList which is a n-len thing """
        return 1
    
    def __repr__(self):
        return u"\n\t [Expr[ "+ unicode(self.term)+ u"] " + \
               Token.token_types[self.binop.kind] + \
               u"\t NextExpr [" + unicode(self.next_expr) + u"]]"

    def do_binop(self,opr1,opr2, binop):
        self.dbg_msg(u" Doing binary operator " + Token.token_types[binop])
        if binop == Token.PLUS:
            self.dbg_msg("addition")
            val = (opr1+opr2)
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
        self.dbg_msg("value = "+unicode(val))
        return val

    @staticmethod
    def normalize_values( obj, term, env ):
        if ( hasattr(term,'evaluate') ):
            if ( isinstance(term,Number) ): #work for both Number, and derived Boolean class
                tval = term.num
            elif ( isinstance(term,String) ):
                tval = term.string                            
            else:
                raise RuntimeException( " cannot normalize token; unknown clause,"+unicode(term)+", to evaluate @ "+obj.get_pos());
        else:
            tval = term #float cast not required.
        return tval
    
    def evaluate(self,env):
        term=self.term.evaluate(env)
        self.dbg_msg(u" "+unicode(term)+u" "+ unicode(term.__class__))
        if self.binop.kind in Token.BINOP:
            tnext = self.next_expr.evaluate(env)
            tval = Expr.normalize_values( self, term, env)
            tval2 = Expr.normalize_values( self, tnext, env)
            self.dbg_msg(u" "+unicode( tval)+ " "+unicode(tval2)+ u" " + unicode(tval2.__class__))
            try:
                term = self.do_binop(tval, tval2, self.binop.kind)
            except Exception as binOp_Except:
                raise RuntimeException(u"binary operation "+unicode(self.term)+unicode(self.binop)+unicode(self.next_expr)+u" failed with exception "+unicode(binOp_Except))
        else:
            raise RuntimeException(u" unknown Binary Operation - Binary operation "+unicode(self.binop)+u" not supported")
        self.dbg_msg(u"term = "+unicode(term)+u" "+unicode(term.__class__))
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
        return u"\n\t [ReturnStmt[ "+ unicode(self.rvalue)+ u"]]\n"

    def evaluate(self,env):
        rhs=self.rvalue.evaluate(env)
        self.dbg_msg(u"return statement evaluated to "+unicode(rhs))
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
        return u"\n\t [BreakStmt]\n"

    def evaluate(self,env):
        self.dbg_msg(u"break statement")
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
        return u"\n\t [ContinueStmt]\n"

    def evaluate(self,env):
        self.dbg_msg(u"continue statement")
        env.set_continue()
        return None
    
    def visit(self, walker):
        walker.visit_continue_stmt(self)
        return

class ElseStmt(Stmt):
    def __init__(self,stmt,l,c, dbg):
        Stmt.__init__(self,l,c,dbg)
        self.stmt = stmt
        self.class_name = u"ElseStmt"

    def __repr__(self):        
        return u"\t [ElseStmt ["+unicode(self.stmt) + u"]]\n"
    
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
        rval = u"\t\n [IfStmt[["+unicode(self.expr)+ u"]] "+unicode(self.body)
        if ( self.next_stmt ):
            try:
                self.dbg_msg( u" ".join([unicode(self.next_stmt),unicode(self.next_stmt.__class__),u"***"]) )
                rval = rval + u"<<Nxt>>" + unicode(self.next_stmt)
            except UnicodeEncodeError as uc_err:
                print(unicode(uc_err))
                raise uc_err
            pass
        rval = rval + u"]"
        return rval

    def set_body(self,body):
        self.body = body
    
    def append_stmt(self,stmt):
        self.next_stmt.append(stmt)
        return
        
    def set_next_stmt(self, stmt):
        self.next_stmt = stmt
    
    def evaluate(self,env):
        self.dbg_msg( u"Eval-if-stmt" + unicode(self.expr) )
        rval = None
        self.dbg_msg(u"eval-if stmt")
        if ( self.is_true_value ( self.expr.evaluate(env) ) ):
            self.dbg_msg(u"ifstmt: true condition")
            rval = self.body.evaluate( env )
            return rval
        self.dbg_msg(u"ifstmt: false condition")
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
        rval = u"\t\n [%s[["%unicode(self.__class__)+unicode(self.expr)+ u"]] "+unicode(self.body) +u"]"
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
        self.dbg_msg("exiting While-stmt with rval="+unicode(rval))
        return rval

    def visit(self,walker):
        walker.visit_while_stmt(self)
        return

class DoWhileStmt(WhileStmt):
    """ do stmtlist  while ( exp )"""
    def __init__(self,expr,body,l,c,dbg=False):
        WhileStmt.__init__(self,expr,body,l,c,dbg)
        
    def __repr__(self):
        return u"[DoWhileStmt[expr="+unicode(self.expr)+u",body="+unicode(self.body)+"]]"
    
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
        self.dbg_msg("exiting Do-While-stmt with rval="+unicode(rval))
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
        rval = u"\t\n [ForStmt[[ ("+unicode(self.expr_init)+"; "+\
            unicode(self.expr_cond) + "; " +\
            unicode(self.expr_update)+") ]] " + unicode(self.body) +"]"
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
        self.dbg_msg(u"exiting For-stmt with rval="+unicode(rval))
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
        return u"\n\t [AssignStmt[ "+ unicode(self.lvalue)+u"] " + \
               Token.token_types[self.assignop.kind] + \
               u"\t Expr [" + unicode(self.rvalue) + u"]]"

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
            self.dbg_msg(u"assignop: rhs = "+unicode(self.rvalue) )
            rhs = self.rvalue.evaluate(env)
            self.do_assignop(self.lvalue,
                             rhs,
                             self.assignop.kind, env)            
            self.dbg_msg(u"assignop lvalue ["+unicode(self.lvalue) \
                             +u"] = ["+unicode(rhs) + \
                             u"( saved as ) " + \
                             unicode(self.lvalue))
                             #unicode(env.get_id(self.lvalue.id)) )
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
        return u"\n\t [PrintStmt[ "+ unicode(self.exprlst)+u"]]"

    def do_printop(self,env):
        val = self.exprlst.evaluate( env  )
        if hasattr(val,'evaluate') :
            assert( False )
            val = val.evaluate( env )
        print(val) #this prints to output
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
        return u"\n\t [EvalStmt[ "+ unicode(self.expr)+u"/"+unicode((self.expr.__class__))+u"]]"

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
        return "\n\t [ArgList["+ ",".join(map(unicode,self.args))+"]]"

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
        return "\n\t [ValueList["+ ",".join(map(unicode,self.args))+"]]"

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
        self.dbg_msg(u"==>"+unicode(stmt_x.__class__))
        self.dbg_msg(u"adding new statement " + unicode(stmt_x.__class__) )
        self.List.append(stmt_x)
        return
    
    def __repr__(self):
        rval = u"\t [StmtList[ "+ u"\n ".join(map(unicode,self.List)) + u"]]\n"
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
        self.dbg_msg( u"function "+fname+u" was defined" )
        
    def dbg_msg(self, msg):
        if ( self.debug ):
            print(u"## ",msg)
        return

    def __repr__(self):
        return u"\n\t [Function[ "+ unicode(self.name)+u"( " + \
            unicode(self.arglist) + u")]\n" + \
            u"\t Body [" + unicode(self.body) + u"]]\n"
    
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
