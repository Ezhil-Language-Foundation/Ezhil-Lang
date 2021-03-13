# -*- coding: utf-8 -*-
# (C) 2013 Muthiah Annamalai
# 
# This file is part of Ezhil Language test suite
# to verify behavior of interactive interpreter

# setup the paths
import ezhiltests
from ezhiltests import TestInteractiveEzhil

# helper functions for testsuites
import unittest
from test import test_support

import ezhil

class Interactive2(unittest.TestCase):
    def test_numbers_and_printing(self):
        code = u"""
        1 + 1
        1 - 1
        1 + 2 - 3
    """
        TestInteractiveEzhil.create_and_test(code)

class Interactive(unittest.TestCase):
    def test_numbers_and_printing(self):
        code = u"""
      1 + 1
            பதிப்பி 10 + 10
            பதிப்பி 1/10.0
            பதிப்பி "1) சேர்"
            பதிப்பி "2) கழி"
            பதிப்பி "3) பெருக்கு"
            பதிப்பி "4) வகு"
            பதிப்பி "5) வெளியேற"
            பதிப்பி "வணக்கம் உலகம்!"
            பதிப்பி "இது என் முதல் எழில் நிரல்"
            பதிப்பி "******* வணக்கம்! மீண்டும் சந்திப்போம் *******"
    """
        TestInteractiveEzhil.create_and_test(code)

if __name__ == '__main__':    
    unittest.main()
