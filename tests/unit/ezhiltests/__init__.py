# (C) 2013 Muthiah Annamalai
# 
# This file is part of Ezhil Language project
# 
# path manipulation magic sets up the current development verison of ezhil
# as the library from the "ezhil-lang/tests/unit" path.

import sys, os
import unittest

ezhil_path = (os.sep).join(os.getcwd().split( os.sep )[:-2])
#print ezhil_path
sys.path.insert(0,ezhil_path)

import ezhil
from  .EzhilTestRunner import TestEzhil, TestEzhilException, TestInteractiveEzhil, TestTimeoutEzhil, QuietTestCase
