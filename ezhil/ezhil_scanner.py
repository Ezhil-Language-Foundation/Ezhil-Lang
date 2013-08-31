#!/usr/bin/python
## -*- coding: utf-8 -*-
## 
## (C) 2008, 2013 Muthiah Annamalai
## Licensed under GPL Version 3
##
## This module is the scanner for the Ezhil language.
## It contains classes EzhilLex.
## 

from EzhilUtils import *
import re
from scanner import Token, Lexeme, Lex
from tamil import has_tamil, istamil, istamil_alnum
from errors import ScannerException

class EzhilLexeme(Lexeme):
    """ Ezhil Lexeme - """ 
    def __init__(self,val,kind,fname=""):
        Lexeme.__init__(self,val,kind,fname)

    def get_kind(self):
        return str(self.val)+str(self.kind)

    def __repr__(self):
        return " %s [%s] Line=%d, Col=%d in File %s "% \
            (str(self.val),self.get_kind(), \
                self.line,self.col,self.fname)


class EzhilToken( Token):
    """ add '@' token in extending the Token type """    
    FORBIDDEN_FOR_IDENTIFIERS = [ "]","["," ",",", "\t","\r","\n","/", "-","+","^","=","*",")","(",">","<","&","&&","|","||","!","%","{","}",";" ]
    Token.token_types.append("@")
    Token.ATRATEOF = len(Token.token_types)    
    
    Token.token_types.append("FOREACH|ஒவ்வொன்றாக")
    Token.FOREACH = len(Token.token_types)
        
    Token.token_types.append("IN|இல்")
    Token.IN = Token.COMMA #short-circuit!
    
    Token.token_types.append("DOWHILE|முடியேனில்")
    Token.DOWHILE = len(Token.token_types)

    @staticmethod
    def is_keyword(kind):
        if Token.is_keyword(kind):
            return True
        if Token.get_name(kind) in ["FOREACH","DOWHILE"]:
            return True
        return False

## SCANNER

class EzhilLex ( Lex ) :
    """ Lex Tamil characters : RAII principle - lex on object construction"""
    
    def __init__(self,fname=None,dbg=False):
        Lex.__init__(self,fname,dbg)
        
    def get_lexeme(self,chunks , pos):        
        if chunks == None:
            return None
        if ( self.debug ): print("chunks",chunks)
        if chunks == "பதிப்பி":
            tval = EzhilLexeme(chunks,EzhilToken.PRINT )
        elif chunks == "தேர்ந்தெடு":
            tval = EzhilLexeme(chunks,EzhilToken.SWITCH )
        elif chunks == "தேர்வு":
            tval = EzhilLexeme(chunks,EzhilToken.CASE )
        elif chunks == "ஏதேனில்":
            tval = EzhilLexeme(chunks,EzhilToken.OTHERWISE )
        elif chunks == "ஆனால்":
            tval = EzhilLexeme( chunks, EzhilToken.IF )
        elif chunks == "இல்லைஆனால்":
            tval = EzhilLexeme( chunks, EzhilToken.ELSEIF )
        elif chunks == "இல்லை":
            tval = EzhilLexeme( chunks, EzhilToken.ELSE )
        elif chunks == "ஆக":
            tval = EzhilLexeme( chunks, EzhilToken.FOR )
        elif chunks == "ஒவ்வொன்றாக":
            tval = EzhilLexeme( chunks, EzhilToken.FOREACH )
        elif chunks == "இல்":
            tval = EzhilLexeme( chunks, EzhilToken.COMMA )
        elif chunks == "வரை":
            tval = EzhilLexeme( chunks, EzhilToken.WHILE )
        elif chunks == "செய்":
            tval = EzhilLexeme( chunks, EzhilToken.DO )
        elif chunks == "முடியேனில்":
            tval = EzhilLexeme( chunks, EzhilToken.DOWHILE )
        elif chunks == "பின்கொடு":
            tval=EzhilLexeme(chunks,EzhilToken.RETURN)
        elif chunks == "முடி":
            tval=EzhilLexeme(chunks,EzhilToken.END)
        elif chunks == "நிரல்பாகம்":
            tval=EzhilLexeme(chunks,EzhilToken.DEF)
        elif chunks == "தொடர்":
            tval=EzhilLexeme(chunks,EzhilToken.CONTINUE)
        elif chunks == "நிறுத்து":
            tval=EzhilLexeme(chunks,EzhilToken.BREAK)
        elif chunks == "@":
            tval=EzhilLexeme(chunks,EzhilToken.ATRATEOF)
        elif chunks == "=":
            tval=EzhilLexeme(chunks,EzhilToken.EQUALS)
        elif chunks == "-":
            tval=EzhilLexeme(chunks,EzhilToken.MINUS)
        elif chunks == "+":
            tval=EzhilLexeme(chunks,EzhilToken.PLUS)
        elif chunks == ">":
            tval=EzhilLexeme(chunks,EzhilToken.GT)
        elif chunks == "<":
            tval=EzhilLexeme(chunks,EzhilToken.LT)
        elif chunks == ">=":
            tval=EzhilLexeme(chunks,EzhilToken.GTEQ)
        elif chunks == "<=":
            tval=EzhilLexeme(chunks,EzhilToken.LTEQ)
        elif chunks == "==":
            tval=EzhilLexeme(chunks,EzhilToken.EQUALITY)
        elif chunks == "!=":
            tval=EzhilLexeme(chunks,EzhilToken.NEQ)
        elif chunks == "*":
            tval=EzhilLexeme(chunks,EzhilToken.PROD)
        elif chunks == "/":
            tval=EzhilLexeme(chunks,EzhilToken.DIV)
        elif chunks == ",":
            tval=EzhilLexeme(chunks,EzhilToken.COMMA)
        elif chunks == "(":
            tval=EzhilLexeme(chunks,EzhilToken.LPAREN)
        elif chunks == ")":
            tval=EzhilLexeme(chunks,EzhilToken.RPAREN)
        elif chunks == "[":
            tval=EzhilLexeme(chunks,EzhilToken.LSQRBRACE)
        elif chunks == "]":
            tval=EzhilLexeme(chunks,EzhilToken.RSQRBRACE)
        elif chunks == "{":
            tval=Lexeme(chunks,Token.LCURLBRACE)
        elif chunks == "}":
            tval=Lexeme(chunks,Token.RCURLBRACE)
        elif chunks == ":":
            tval=Lexeme(chunks,Token.COLON)
        elif chunks == "%":
            tval=EzhilLexeme(chunks,EzhilToken.MOD)
        elif chunks == "^":
            tval=EzhilLexeme(chunks,EzhilToken.EXP)
        elif chunks == "&&":            
            tval=Lexeme(chunks,EzhilToken.LOGICAL_AND)
        elif chunks == "&":
            tval=Lexeme(chunks,EzhilToken.BITWISE_AND)
        elif chunks == "||":
            tval=Lexeme(chunks,EzhilToken.LOGICAL_OR)
        elif chunks == "|":
            tval=Lexeme(chunks,EzhilToken.BITWISE_OR)
        elif chunks == "!":
            tval=Lexeme(chunks,EzhilToken.LOGICAL_NOT)
        elif ( chunks[0] == "\"" and chunks[-1] == "\"" ):
            tval = EzhilLexeme( chunks[1:-1], EzhilToken.STRING )
        elif isdigit(chunks[0]) or chunks[0]=='+' or chunks[0]=='-':
            #tval=EzhilLexeme(float(chunks),EzhilToken.NUMBER)
            # deduce a float or integer            
            if ( chunks.find('.') >= 0 or chunks.find('e') >= 0 or chunks.find('E') >= 0 ):
                tval=EzhilLexeme(float(chunks),EzhilToken.NUMBER)
            else:
                tval=EzhilLexeme(int(chunks),EzhilToken.NUMBER)
        elif isalpha(chunks[0]) or has_tamil(chunks) or chunks[0] == '_':
            ## check for tamil/english/mixed indentifiers even starting with a lead '_'
            tval=EzhilLexeme(chunks,EzhilToken.ID)
        else:
            raise ScannerException("Lexical error: " + str(chunks) + " at Line , Col "+str(self.get_line_col( pos )) +" in file "+self.fname )
        
        [l,c]=self.get_line_col( pos )
        tval.set_line_col( [l,c] )
        tval.set_file_name( self.fname )
        self.tokens.append( tval )
        
        if ( self.debug ): print("Lexer token = ",str(tval))
        
        return l
    
    def tokenize(self,data=None):
        """ do hard-work of tokenizing and
        put EzhilLexemes into the tokens[] Q """
        if ( self.stdin_mode ):
            if ( self.debug ): print(self.tokens)
            ## cleanup the Q for stdin_mode of any EOF that can remain.
            if ( len(self.tokens) != 0 ):
                self.match( EzhilToken.EOF )
            if( len(self.tokens) != 0 ):
                raise ScannerException("Lexer: token Q has previous session tokens ")
            self.tokens = list()
        else:
            data = "".join(self.File.readlines())
        if ( self.debug ): print(data)
        idx = 0
        tok_start_idx = 0
        
        while ( idx < len( data ) ):
            c = data[idx]
            if  ( c == ' 'or c == '\t' or c == '\n'):
                if ( c == '\n' ):
                    ##actual col = idx - col_idx
                    self.update_line_col(idx)
                idx = idx + 1
            elif ( c == '\r' ):
                idx = idx + 1
                continue
            elif ( c == '#' ):
                ## single line skip comments like Python/Octave
                start = idx;
                while ( idx < len( data ) and not (data[idx] in ['\r','\n']) ):
                    idx = idx + 1
                if ( data[idx] == '\r' ):
                    idx = idx + 1
                end = idx
                self.comments[self.line]= data[start:end]
            elif ( isdigit(c) ): #or c == '+' or c == '-'  ):
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
                in_sci_notation = False
                while ( ( idx < len( data) )
                            and ( isdigit(data[idx]) or data[idx] in ['+','-','e','E','.']) ):
                    if ( data[idx] in ['+','-'] and not in_sci_notation ):
                        break;
                    elif( data[idx] in ['e','E'] ):
                        in_sci_notation = True
                    num = num + data[idx]
                    idx = idx + 1
                self.get_lexeme( num , tok_start_idx  )
            elif ( c == "\"" ):
                tok_start_idx = idx 
                s = c; idx = idx + 1
                while ( idx < len( data ) and
                         ( data[idx] != '\"' ) ):
                    if ( data[idx] == '\\' ):
                        idx = idx + 1
                        if ( data[idx] == 'n' ):
                            s = s + '\n'
                        elif ( data[idx] == 't' ):
                            s = s + '\t'
                        else:
                            s = s + data[idx]
                    else:
                        s = s + data[idx]
                    idx  = idx + 1
                s = s+data[idx]
                idx  = idx + 1
                self.get_lexeme( s , tok_start_idx )
            elif ( istamil( c ) or isalpha( c ) or c == '_' ):
                tok_start_idx = idx 
                s = c; idx = idx + 1
                while ( ( idx < len( data ) )
                            and ( not data[idx] in EzhilToken.FORBIDDEN_FOR_IDENTIFIERS ) ):
                    s = s + data[idx]
                    idx = idx + 1                
                self.get_lexeme( s , tok_start_idx )
            elif ( c in self.unary_binary_ops ):
                tok_start_idx = idx                 
                if ( len(data) > ( 1 + idx  ) 
                     and data[idx+1] in ['=','|','&'] ):
                    c = c +data[idx+1]
                    idx = idx + 1
                self.get_lexeme(  c , tok_start_idx )
                idx = idx + 1
            elif c == ";":
                # treat as newline
                idx = idx + 1
                continue
            else:
                tok_start_idx = idx 
                idx = idx + 1
                self.get_lexeme( c , tok_start_idx )
        
        tok_start_idx = idx
        ## close the file if not stdin_mode
        if ( not self.stdin_mode ): self.File.close()
        
        ## and manually add an EOF statement.
        eof_tok = EzhilLexeme("",EzhilToken.EOF )
        eof_tok.set_line_col( self.get_line_col( tok_start_idx ) )
        self.tokens.append( eof_tok )
        if ( self.debug ):  print("before reverse"); self.dump_tokens()
        self.tokens.reverse()
        if ( self.debug ):  print("after reverse"); self.dump_tokens()
        return
