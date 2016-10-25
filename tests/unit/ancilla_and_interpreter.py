# -*- coding: utf-8 -*-
# (C) 2013, 2016 Muthiah Annamalai
# 
# This file is part of Ezhil Language test suite
# 
from __future__ import print_function
# setup the paths
from ezhiltests import *

# helper functions for testsuites
from test import test_support

import ezhil

class Ancilla(unittest.TestCase):
    def test_latest_version(self):     
        assert( ezhil.version() >= 0.82 )

    def test_credits(self):
        assert( ezhil.credits().find("Annamalai") >= 0 )

    def test_start_method(self):
        assert( callable(ezhil.start) )
    
    # 40 keywords/tokens for Ezhil Language
    def test_keywords(self):
        self.assertEqual( len(zip(*ezhil.keywords())) , 49)
    
class Interpreter(unittest.TestCase):
    def test_run_addition(self):
        TestEzhil.create_and_test("1+5")

class WebEzhil(unittest.TestCase):
    def test_timeout_infinite_loop(self):
        infinite_loop_code = u"""
# மாதிரி =>  முடிவிலா சுழற்சி
# கூகிள் மொழிபெயர்ப்பு பயன்படுத்தி

i = 0
@( i >= 0 ) வரை
 i = i + 1
முடி
"""
        # should timeout soon enough - 10s
        TestTimeoutEzhil.create_and_test(infinite_loop_code,timeout=4)

if __name__ == '__main__':    
    unittest.main()
