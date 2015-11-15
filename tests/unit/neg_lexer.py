# -*- coding: utf-8 -*-
# (C) 2015 Muthiah Annamalai
# 
# This file is part of Ezhil Language test suite
# 

# setup the paths
import ezhiltests
from ezhiltests import TestEzhilException, QuietTestCase, ezhil
from  ezhil.errors import ScannerException
from random import choice

# helper functions for testsuites
import unittest
from test import test_support

# this test suite contains negative tests, to trap the 
# correct error behavior of Ezhil language

class IdentifierNeg(QuietTestCase):
    def get_filename(self):
        return 'dummy_IdentifierNeg.txt'
    
    def test_lexer_error(self):        
        for wrongID in [u"Turing'",u"babb@ge",u"Ada'",u"Grace'",u"Hopper\"",u"Li$kov",u"sch@figoldw@$$er"]:
            TestEzhilException.create_and_test(wrongID,ScannerException,"is not valid for identifier")
        return
    
    def test_invalid_id_lex(self):
        for wrongID in [u"é.€ = 1.23", u"பதிப்பி é.€","Raj.Reddy","Edsger.Dijkstra"]:
            TestEzhilException.create_and_test(wrongID,ScannerException,"Lexical error")
        return
    
    def test_neg_lex(self):
        for wrongID in [u"λஃ = 5",u"x☺ = 5 #not legal"]:
            TestEzhilException.create_and_test(wrongID,ScannerException,"Lexical error")
        return

if __name__ == "__main__":
    unittest.main()
