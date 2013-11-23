#!/usr/bin/python
##
## (C) 2007, 2008, 2013 Muthiah Annamalai
## Licensed under GPL Version 3
##
## This module is the custom exceptions for
## the exprs language

## Exception states
class ErrorException(Exception):
    def __repr__(self):
        return str(self.args)+"\n"

    def __str__(self):
        ##works in python2.6
        return " ".join(self.args)


class ScannerException(ErrorException):
    def __init__(self,desc):
        self.args = ["Lexical error:", desc ]

class RuntimeException(ErrorException):
    def __init__(self,desc):
        self.args = ["Run-time error", desc ]

class ParseException(ErrorException):
    def __init__(self,desc):
        self.args = ["Parse error:", desc ]


class TimeoutException(Exception):
        def __init__(self,timeout):
            Exception.__init__(self)
            self.timeout = timeout

        def __str__(self):
            return "process exceeded timeout of " + str(self.timeout) + "s"
