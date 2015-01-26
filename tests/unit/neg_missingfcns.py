# -*- coding: utf-8 -*-
# (C) 2014 Muthiah Annamalai
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

class MissingFcnsNeg(unittest.TestCase):
    def test_system_OS_function(self):
        exprCode  = u"""
# (C) முத்தையா அண்ணாமலை 2014
system("ls -lrt")
system("cat /etc/passwd")
""" #missing end function statement
        TestEzhilException.create_and_test_spl(exprCode,RuntimeException,"system")
        
    def test_getenv_OS_module_fcn(self):        
        exprCode  = u"""
# (C) முத்தையா அண்ணாமலை 2013
getenv("SHELL") #not avaiable in safe mode
""" #missing end function statement
        TestEzhilException.create_and_test_spl(exprCode,RuntimeException,"getenv")

    def test_globals_deleted_fcn(self):        
        exprCode  = u"""
# (C) முத்தையா அண்ணாமலை 2013
globals() #not avaiable in safe mode
""" #missing end function statement
        TestEzhilException.create_and_test_spl(exprCode,RuntimeException,"globals")

if __name__ == '__main__':
    test_support.run_unittest(MissingFcnsNeg)
