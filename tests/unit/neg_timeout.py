# -*- coding: utf-8 -*-
# (C) 2013-2015 Muthiah Annamalai
#
# This file is part of Ezhil Language test suite
#

# setup the paths
import ezhiltests
from ezhiltests import TestEzhilException, ezhil
from ezhil.errors import RuntimeException

# helper functions for testsuites
import unittest

class InfiniteTimeoutTest(unittest.TestCase):
    def test_timeout(self):
        self.do_timeout_test("infi.n")

    def test_quiet_timeout(self):
        self.do_timeout_test("purinfi.n")

    # utility function
    def do_timeout_test(self,fname):
        with self.assertRaises(RuntimeException) as e:
            ezhil.ezhil_timeout_exec(fname)
        self.assertTrue( '13 (seconds)' in str(e.exception))

if __name__ == '__main__':
    unittest.main()
