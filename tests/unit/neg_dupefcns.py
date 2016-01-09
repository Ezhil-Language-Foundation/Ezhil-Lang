# -*- coding: utf-8 -*-
# (C) 2014-2016 Muthiah Annamalai
# 
# This file is part of Ezhil Language test suite
# 

# setup the paths
import ezhiltests
from ezhiltests import TestEzhilException, ezhil
from  ezhil.errors import RuntimeException

# helper functions for testsuites
import unittest
from test import test_support

# this test suite contains negative tests, to trap the 
# correct error behavior of Ezhil language

class DupeFcnsNeg(unittest.TestCase):
    def test_dupe_fcns(self):        
        exprCode  = u"""
# (C) முத்தையா அண்ணாமலை 2013

நிரல்பாகம்  fact ( n )
  @( n == 0 ) ஆனால்
            பின்கொடு  1
     இல்லை
            பின்கொடு    n*fact( n - 1 )
    முடி
முடி

நிரல்பாகம்  fact ( n )
  @( n == 0 ) ஆனால்
            பின்கொடு  1
     இல்லை
            பின்கொடு    n*fact( n - 1 )
    முடி
முடி

பதிப்பி fact(5)
""" #we raise exception on duplicate fcns
        TestEzhilException.create_and_test_spl_safe_mode(exprCode,Exception,"multiply defined")

if __name__ == '__main__':
    test_support.run_unittest(DupeFcnsNeg)
