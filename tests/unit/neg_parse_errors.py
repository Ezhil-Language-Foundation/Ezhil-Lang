# -*- coding: utf-8 -*-
# (C) 2013 Muthiah Annamalai
# 
# This file is part of Ezhil Language test suite
# 

# setup the paths
import ezhiltests
from ezhiltests import TestEzhilException, ezhil
from  ezhil.errors import ParseException

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
        TestEzhilException.create_and_test(exprCode,ParseException,[r"Expected Number, found something","Line=7, Col=5"])
        
    
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

if __name__ == '__main__':    
    test_support.run_unittest(ExprNeg,StmtNeg)
