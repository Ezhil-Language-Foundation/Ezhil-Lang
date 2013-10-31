# setup the paths
import ezhiltests

# helper functions for testsuites
import unittest
from test import test_support

import os
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
        fp = open("hello.n","w")
        fp.write("1 + 5\n")
        fp.write("pi()*3.14159\n")
        fp.write("exit\n")
        fp.close()
        
        try:
            ezhil.EzhilFileExecuter("hello.n",False,True)
        except Ex:
            raise Ex
        finally:
            os.unlink("hello.n")
        
if __name__ == '__main__':    
    test_support.run_unittest(Ancilla,Interpreter)

