# -*- coding: utf-8 -*-
# (C) 2018 Muthiah Annamalai
# 
# This file is part of Ezhil Language test suite
# 

# setup the paths
import ezhiltests
from ezhil import ezhil_eval
from ezhil.errors import RuntimeException

# helper functions for testsuites
import unittest

# this test suite contains negative tests, to trap the 
# correct error behavior of Ezhil language

debug = False

class SimpleNegTests(unittest.TestCase):
    def test_wrong_identifier(self):
        code = "f01234\n"
        with self.assertRaises(RuntimeException) as e:
            ezhil_eval(code)
        self.assertTrue('Run-time error: Cannot Find Identifier f01234 at Line 1, col 0.' in str(e.exception))
        return

if __name__ == "__main__":
    unittest.main()
