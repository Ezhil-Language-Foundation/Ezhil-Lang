# setup the paths
import ezhiltests
from ezhiltests import TestEzhil

# helper functions for testsuites
import unittest
from test import test_support

import ezhil

class Ancilla(unittest.TestCase):
    def test_latest_version(self):     
        assert( ezhil.version() > 0.7 )

    def test_credits(self):
        assert( ezhil.credits().find("Annamalai") >= 0 )

    def test_start_method(self):
        assert( callable(ezhil.start) )
    
class Interpreter(unittest.TestCase):
    def test_run_addition(self):
        TestEzhil.create_and_test("1+5")
    
if __name__ == '__main__':    
    test_support.run_unittest(Ancilla,Interpreter)
