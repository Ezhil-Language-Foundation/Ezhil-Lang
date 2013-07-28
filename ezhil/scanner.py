#!/usr/bin/python
##
## (C) 2007, 2008 Muthiah Annamalai
## Licensed under GPL Version 3
##
## This module is the scanner for the exprs language.
## It contains classes Token, Lexeme, and  Lex.
## 
from EzhilUtils import *
from errors import ScannerException
import re

## SCANNER
class Token:
    token_types=["EOF","ID","NUMBER","PRINT","PLUS","MINUS",
                 "PROD","DIV","LPAREN","RPAREN","COMMA",
                 "EQUALS","END","DEF","RETURN","IF","ELSEIF","ELSE",
                 "DO","WHILE","FOR","STRING",">","<",">=","<=","!=",
                 "==","[","]","^","%","BREAK","CONTINUE","SWITCH",
                 "CASE","OTHERWISE","&&","||","&","|","!"]

    def get_name(kind):
        """ used in reporting errors in match() on parsing stage """
        if ( kind >= 0 and kind < len(Token.token_types) ):
            return Token.token_types[kind]
        raise ScannerException("Index out of bounds. Unknown token "+str(kind))
        return None
    get_name = staticmethod(get_name)
    
    EOF = 0
    ID = 1
    NUMBER = 2
    PRINT = 3
    PLUS = 4
    MINUS = 5
    PROD = 6
    DIV = 7
    LPAREN = 8
    RPAREN = 9
    COMMA = 10
    EQUALS = 11
    END = 12
    DEF = 13
    RETURN = 14
    IF = 15
    ELSEIF = 16
    ELSE   = 17
    DO = 18
    WHILE = 19
    FOR = 20
    STRING = 21
    GT = 22
    LT = 23
    GTEQ = 24
    LTEQ = 25
    NEQ = 26
    EQUALITY = 27
    LSQRBRACE = 28
    RSQRBRACE = 29
    EXP = 30
    MOD = 31
    BREAK = 32
    CONTINUE = 33
    SWITCH = 34
    CASE = 35
    OTHERWISE = 36
    LOGICAL_AND = 37
    LOGICAL_OR = 38
    BITWISE_AND = 39
    BITWISE_OR = 40
    LOGICAL_NOT = 41
    
    UNARYOP = [LOGICAL_NOT]
    ADDSUB = [PLUS, MINUS]
    MULDIV = [PROD,DIV]
    COMPARE = [ GT, LT, GTEQ, LTEQ, NEQ, EQUALITY ]
    EXPMOD = [EXP, MOD]
    BITWISE_AND_LOGICAL = [LOGICAL_AND, LOGICAL_OR, BITWISE_AND, BITWISE_OR];
    BINOP = []
    for i in [ADDSUB, MULDIV, COMPARE, EXPMOD, BITWISE_AND_LOGICAL]:
        BINOP.extend( i )
    ASSIGNOP = [EQUALS]
    

class Lexeme:
    def __init__(self,val,kind,fname=""):
        self.val = val
        self.kind = kind
        self.line = -1
        self.col = -1
        self.fname = fname

    def set_file_name(self,file_name):
        self.fname = file_name
        return True
        
    def get_line_col(self):
        return [self.line, self.col]

    def set_line_col(self, lc):
        [l, c] = lc
        self.line = l
        self.col = c
        
    def __repr__(self):
        return " %s Line=%d, Col=%d in File %s "% \
            (str(self.val),self.line,self.col,self.fname)

class Lex:
    """ Lexer automatically starts lexing on init.
    Maybe use some Library module? """

    def __init__(self,fname=None,dbg=False):
        self.stdin_mode = False
        self.debug = dbg;
        if ( fname ):
            self.fname = fname
            self.File=open(fname)
        else:
            self.fname = "<STDIN>"
            self.stdin_mode = True
        ##actual col = idx - col_idx
        self.line = 1 
        self.col_idx = 0 
        ##contains lexeme's in reverse order
        ##for popping is elegant.
        self.tokens=[]
        self.spc=re.compile("\s+")
        self.newlines=re.compile("\n+")
        self.unary_binary_ops = \
            [ '+','-','=','*','/','>','<','%','^','!=','!','&&','||','|','&','!']
        ## need to be the last on init & only for files
        if ( not self.stdin_mode  ): self.tokenize()
        ## REPL loop can call tokenize_string whenever it
        ## desires so.
        
    def __repr__(self):
        for idx in range(0,len(self.tokens)):
            print("%d] %s"%(idx,repr(self.tokens.pop())))
        return ""

    def get_lexeme(self,chunks , pos):
        if chunks == None:
            return None

        if chunks == "print":
            tval=Lexeme(chunks,Token.PRINT)
        elif chunks == "if":
            tval = Lexeme( chunks, Token.IF )
        elif chunks == "elseif":
            tval = Lexeme( chunks, Token.ELSEIF )
        elif chunks == "else":
            tval = Lexeme( chunks, Token.ELSE )
        elif chunks == "for":
            tval = Lexeme( chunks, Token.FOR )
        elif chunks == "while":
            tval = Lexeme( chunks, Token.WHILE )
        elif chunks == "do":
            tval = Lexeme( chunks, Token.DO )
        elif chunks == "return":
            tval=Lexeme(chunks,Token.RETURN)
        elif chunks == "end":
            tval=Lexeme(chunks,Token.END)
        elif chunks == "def":
            tval=Lexeme(chunks,Token.DEF)
        elif chunks == "continue":
            tval=Lexeme(chunks,Token.CONTINUE)
        elif chunks == "break":
            tval=Lexeme(chunks,Token.BREAK)
        elif chunks == "=":
            tval=Lexeme(chunks,Token.EQUALS)
        elif chunks == "-":
            tval=Lexeme(chunks,Token.MINUS)
        elif chunks == "+":
            tval=Lexeme(chunks,Token.PLUS)
        elif chunks == ">":
            tval=Lexeme(chunks,Token.GT)
        elif chunks == "<":
            tval=Lexeme(chunks,Token.LT)
        elif chunks == ">=":
            tval=Lexeme(chunks,Token.GTEQ)
        elif chunks == "<=":
            tval=Lexeme(chunks,Token.LTEQ)
        elif chunks == "==":
            tval=Lexeme(chunks,Token.EQUALITY)
        elif chunks == "!=":
            tval=Lexeme(chunks,Token.NEQ)
        elif chunks == "*":
            tval=Lexeme(chunks,Token.PROD)
        elif chunks == "/":
            tval=Lexeme(chunks,Token.DIV)
        elif chunks == ",":
            tval=Lexeme(chunks,Token.COMMA)
        elif chunks == "(":
            tval=Lexeme(chunks,Token.LPAREN)
        elif chunks == ")":
            tval=Lexeme(chunks,Token.RPAREN)
        elif chunks == "[":
            tval=Lexeme(chunks,Token.LSQRBRACE)
        elif chunks == "]":
            tval=Lexeme(chunks,Token.RSQRBRACE)
        elif chunks == "%":
            tval=Lexeme(chunks,Token.MOD)
        elif chunks == "^":
            tval=Lexeme(chunks,Token.EXP)
        elif chunks == "&&":
            tval=Lexeme(chunks,Token.LOGICAL_AND)
        elif chunks == "&":
            tval=Lexeme(chunks,Token.BITWISE_AND)
        elif chunks == "||":
            tval=Lexeme(chunks,Token.LOGICAL_OR)
        elif chunks == "|":
            tval=Lexeme(chunks,Token.BITWISE_OR)
        elif ( chunks[0] == "\"" and chunks[-1] == "\"" ):
            tval = Lexeme( chunks[1:-1], Token.STRING )
        elif isdigit(chunks[0]) or chunks[0]=='+' or chunks[0]=='-':
            # deduce a float or integer
            if ( chunks.find('.') >= 0 or chunks.find('e') >= 0 or chunks.find('E') >= 0 ):
                tval=Lexeme(float(chunks),Token.NUMBER)
            else:
                tval=Lexeme(int(chunks),Token.NUMBER)
            
        elif isalpha(chunks[0]):
            tval=Lexeme(chunks,Token.ID)
        else:
            raise ScannerException("Lexical error: " + str(chunks) + " at Line , Col "+str(self.get_line_col( pos )) +" in file "+self.fname )
        
        [l,c]=self.get_line_col( pos )
        tval.set_line_col( [l,c] )
        tval.set_file_name( self.fname )
        self.tokens.append( tval )
        return l
    
    def update_line_col(self, pos ):
        ## pos is in current token stream
        self.line = self.line + 1
        self.col_idx = pos 

    def get_line_col( self , pos ):
        ## pos is in current token stream
        return [ self.line, pos -  self.col_idx  ]

    def set_line_col(self, lc):
        [l, c] = lc
        self.line = l
        self.col_idx = c

    def tokenize(self,data=None):
        """ do hard-work of tokenizing and
        put Lexemes into the tokens[] Q """
        if ( self.stdin_mode ):
            if ( self.debug ): print(self.tokens)
            ## cleanup the Q for stdin_mode of any EOF that can remain.
            if ( len(self.tokens) != 0 ):
                self.match( Token.EOF )
            if( len(self.tokens) != 0 ):
                raise ScannerException("Lexer: token Q has previous session tokens ")
            self.tokens = list()
        else:
            data = "".join(self.File.readlines())
        
        idx = 0 
        tok_start_idx = 0

        while ( idx < len( data ) ):
            c = data[idx]
            
            if  ( c == ' 'or c == '\t' or c == '\n' ):
                if ( c == '\n' ):
                    ##actual col = idx - col_idx
                    self.update_line_col(idx)
                idx = idx + 1
            elif ( c == '#' ):
                ## single line skip comments like Python/Octave
                while ( idx < len( data ) and data[idx] !='\n' ):
                    idx = idx + 1                    
            elif ( isdigit(c) or c == '+' or c == '-'  ):
                num = c
                tok_start_idx = idx
                idx = idx + 1
                ## FIXME: this prevents you from +.xyz, or -.xyz use 0.xyz 
                ## instead. also may throw an error if we exceed 
                ## buffer-length.                
                if ( c in ['+','-']  and ( idx < len( data ) ) 
                     and not isdigit(data[idx]) ):
                    self.get_lexeme( c , idx )
                    continue
                while ( ( idx < len( data) )
                            and ( isdigit(data[idx]) or data[idx] == '.') ):
                    num = num + data[idx]
                    idx = idx + 1
                self.get_lexeme( num , tok_start_idx  )
            elif ( c == "\"" ):
                tok_start_idx = idx 
                s = c; idx = idx + 1
                while ( idx < len( data ) and
                         ( data[idx] != '\"' ) ):
                    s = s + data[idx]
                    if ( data[idx] == '\\' ):
                        idx = idx + 1
                    idx  = idx + 1
                s = s+data[idx]
                idx  = idx + 1
                self.get_lexeme( s , tok_start_idx )
            elif ( isalpha( c ) ):
                tok_start_idx = idx 
                s = c; idx = idx + 1
                while ( ( idx < len( data ) )
                            and ( isalpha(data[idx]) or isdigit( data[idx] )
                                  or data[idx] in [ "\"", "_" ] ) ):
                    s = s + data[idx]
                    idx = idx + 1
                self.get_lexeme( s , tok_start_idx )
            elif ( c in self.unary_binary_ops ):
                tok_start_idx = idx 
                if ( len(data) > ( 1 + idx  ) 
                     and data[idx+1] in ['=','|','&']  ):
                    c = c +data[idx+1]
                    idx = idx + 1
                self.get_lexeme(  c , tok_start_idx )
                idx = idx + 1
            else:
                tok_start_idx = idx 
                idx = idx + 1
                self.get_lexeme( c , tok_start_idx )
        
        tok_start_idx = idx 

        ## close the file if not stdin_mode
        if ( not self.stdin_mode ): self.File.close()

        ## and manually add an EOF statement.
        eof_tok = Lexeme("",Token.EOF )
        eof_tok.set_line_col( self.get_line_col( tok_start_idx ) )
        self.tokens.append( eof_tok )

        self.tokens.reverse()
        return 
        
    def dump_tokens(self):
        print(" \n".join([str(self.tokens[i]) for i in range(len(self.tokens)-1,-1,-1)]))
        return

    def dequeue(self):
        """ remove Lexeme from the head of Q"""
        ##print "~ ~ match ",repr(self.tokens[-1])
        return self.tokens.pop()
    
    def end_of_tokens(self):
        return (len(self.tokens) == 0)  or (self.peek().kind == Token.EOF )

    def peek(self):
        """ remove Lexeme from the head of Q""" 
        if len(self.tokens) == 0:
            raise ScannerException("tokens[] queue is empty ")
        ##print "**> PEEK-ing, ",self.tokens[-1]
        return self.tokens[-1]

    def match(self,tokval):
        """ if match return value of token """
        if self.peek().kind != tokval:
            ##print self
            raise ScannerException("cannot find token "+ \
                                Token.get_name(tokval) + " got " \
                                + str(self.peek())  \
                                + " instead!")
        return self.dequeue()
