# -*- coding: utf-8 -*-
# (C) 2018 Muthiah Annamalai
# 
# This file is part of Ezhil Language test suite
# 

# setup the paths
from ezhil import ezhil_eval
from ezhil.errors import RuntimeException

# helper functions for testsuites
import unittest

# this test suite contains negative tests, to trap the 
# correct error behavior of Ezhil language

debug = False

class SimpleNegTests(unittest.TestCase):
    def test_wrong_identifier(self):
        e = None
        code = u"f01234\n"
        try:
            ezhil_eval(code)
        except RuntimeException as e:
            pass
        self.assertTrue(isinstance(e,RuntimeException))
        return

if __name__ == u"__main__":
    unittest.main()
