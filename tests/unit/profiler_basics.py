# -*- coding: utf-8 -*-
# (C) 2015 Muthiah Annamalai
# 
# This file is part of Ezhil Language test suite
# 

# setup the paths
import ezhiltests
from ezhiltests import TestEzhilException, QuietTestCase, ezhil
from  ezhil.errors import ScannerException
from  ezhil.profile import Profiler
from random import choice

# helper functions for testsuites
import unittest
from test import test_support

import time

class ProfilerBasics(QuietTestCase):
    def get_filename(self):
        return 'dummy_ProfilerBasics.txt'
    
    def test_basic(self):
            pr = Profiler()
            pr.add_new_function('a',time.time())
            time.sleep(0.25)
            
            pr.add_new_function('b',time.time())
            time.sleep(0.1)
            pr.add_new_function('c',time.time())
            time.sleep(0.1)
            pr.update_function_on_return('c',time.time())
            time.sleep(0.1)
            pr.update_function_on_return('b',time.time())
    
            pr.add_new_function('b',time.time())
            time.sleep(0.25)
            pr.add_new_function('c',time.time())
            time.sleep(0.1)
            pr.update_function_on_return('c',time.time())
            time.sleep(0.1)
            pr.update_function_on_return('b',time.time())
            
            pr.update_function_on_return('a',time.time())
            
            pr.report_stats()
            return

if __name__ == "__main__":
    unittest.main()
