# setup the paths
import ezhiltests
from ezhiltests import TestEzhilException

# helper functions for testsuites
import unittest
from test import test_support

import os
import ezhil


class ExprNeg(unittest.TestCase):
    def test_run_addition(self):
        from  ezhil.errors import ParseException        
        TestEzhilException.create_and_test("1--",ParseException,"Expected Number")
    
if __name__ == '__main__':    
    test_support.run_unittest(ExprNeg)#,StmtNeg)
