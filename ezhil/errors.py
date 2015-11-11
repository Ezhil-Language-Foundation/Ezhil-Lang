#!/usr/bin/python
##
## (C) 2007, 2008, 2013 Muthiah Annamalai
## Licensed under GPL Version 3
##
## This module is the custom exceptions for
## the exprs language

class Messages:
    LEXICAL_ERROR = "Lexical error:"
    RUNTIME_ERROR = "Run-time error:"
    PARSE_ERROR = "Parse error:"
    TIMEOUT_ERROR = "process exceeded timeout of  %s(seconds)"

## Exception states
class ErrorException(Exception):
    def __repr__(self):
        return str(self.args)+"\n"

    def __str__(self):
        ##works in python2.6
        return u" ".join(self.args)


class ScannerException(ErrorException):
    def __init__(self,desc):
        self.args = [Messages.LEXICAL_ERROR, desc ]


class RuntimeException(ErrorException):
    def __init__(self,desc):
        self.args = [Messages.RUNTIME_ERROR, desc ]


class ParseException(ErrorException):
    def __init__(self,desc):
        self.args = [Messages.PARSE_ERROR, desc ]


class TimeoutException(Exception):
        def __init__(self,timeout):
            Exception.__init__(self)
            self.timeout = timeout

        def __str__(self):
            return Messages.TIMEOUT_ERROR%(self.timeout)
