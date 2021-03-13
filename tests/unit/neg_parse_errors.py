# -*- coding: utf-8 -*-
# (C) 2013-2015 Muthiah Annamalai
# 
# This file is part of Ezhil Language test suite
# 

# setup the paths
from ezhiltests import skip_python2_6, TestEzhilException, ezhil
from  ezhil.errors import ParseException, RuntimeException
from ezhil import ezhil_eval

# helper functions for testsuites
import unittest
from test import test_support

# this test suite contains negative tests, to trap the 
# correct error behavior of Ezhil language

class ExprNeg(unittest.TestCase):
    def test_run_addition(self):
        from  ezhil.errors import ParseException        
        for exprCode in ["1--","+1+","2-4/5%","5%5%"]:
            TestEzhilException.create_and_test(exprCode,ParseException,"Expected Number")

class StmtNeg(unittest.TestCase):
    def test_nested_fn(self):
        exprCode = u""" நிரல்பாகம்  fact2 ( n )
    @( n == 0 ) ஆனால்      
            பின்கொடு  1
    இல்லை
            பின்கொடு    n*fact( n - 1 )
    முடி
    நிரல்பாகம்  fact ( n )
        1+1 #nested function
    முடி
முடி""" #error message is bad for nested function case. but alteast it errors out.
        TestEzhilException.create_and_test(exprCode,ParseException,u"Parse error: cannot find token END")
	
    def test_return_stmt_dangling_function(self):
        exprCode  = u"""
# (C) முத்தையா அண்ணாமலை 2013
# இது ஒரு எழில் தமிழ் நிரலாக்க மொழி உதாரணம்
    நிரல்பாகம்  fact2 ( n )
       1+1 #nested function
    முடி
    @( n == 0 ) ஆனால்
            பின்கொடு  1
    இல்லை
            பின்கொடு    n*fact( n - 1 )
    முடி"""
        TestEzhilException.create_and_test(exprCode,ParseException,"return statement outside of function body")
	
    def test_missing_ifstmt(self):
        exprCode  = u"""
# (C) முத்தையா அண்ணாமலை 2013
# இது ஒரு எழில் தமிழ் நிரலாக்க மொழி உதாரணம்
நிரல்பாகம்  fact ( n )
  @( n == 0 )  இல்லை
            பின்கொடு  1
     ஆனால்
            பின்கொடு    n*fact( n - 1 )
    முடி""" #missing end function statement
        TestEzhilException.create_and_test(exprCode,ParseException,"parsing Statement, unknown operators")
        
    def test_missing_end(self):        
        exprCode  = u"""
# (C) முத்தையா அண்ணாமலை 2013
# இது ஒரு எழில் தமிழ் நிரலாக்க மொழி உதாரணம்
நிரல்பாகம்  fact ( n )
  @( n == 0 ) ஆனால்
            பின்கொடு  1
     இல்லை
            பின்கொடு    n*fact( n - 1 )
    முடி""" #missing end function statement
        TestEzhilException.create_and_test(exprCode,ParseException,"cannot find token END")

class TooFewArgsNeg(unittest.TestCase):
    @skip_python2_6
    def test_insufficient_call_args(self):
        exprCode  = u"""
# this is a test for error detection in Ezhil
நிரல்பாகம் function(தேவைஇல்லை)
# என்னவோ செய்ய
பின்கொடு பட்டியல்()
முடி 
function( )
"""
        #missing end function statement
        expected = u"Function '%s' expects %d arguments but received only %d"%(u"function",1,0)
        with self.assertRaises(RuntimeException) as context:
            ezhil_eval(exprCode)
        self.assertTrue(isinstance(context.exception,RuntimeException))
        self.assertTrue(expected in str(context.exception))

if __name__ == '__main__':    
    unittest.main()
