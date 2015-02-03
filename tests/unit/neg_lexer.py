# -*- coding: utf-8 -*-
# (C) 2015 Muthiah Annamalai
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

class IdentifierNeg(unittest.TestCase):
    def test_lexer_error(self):
        from ezhil.errors import ScannerException
        for wrongID in ["Turing'","babb@ge","Ada'","Grace'","Hopper\"","Li$kov","sch@figoldw@$$er"]:
            TestEzhilException.create_and_test(wrongID,ScannerException,"is not valid for identifier")
        return

if __name__ == "__main__":
    unittest.main()
