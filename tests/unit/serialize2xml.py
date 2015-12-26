# -*- coding: utf-8 -*-
# (C) 2015 Muthiah Annamalai
# 
# This file is part of Ezhil Language test suite
# 

# setup the paths
import ezhiltests
from ezhiltests import TestEzhilException, QuietTestCase, ezhil
from ezhil import EzhilInterpreter, EzhilLex
from ezhil.ezhil_serializer import SerializerXML

# helper functions for testsuites
import unittest
from test import test_support

import time

class SerializeToXML(QuietTestCase):
    def get_filename(self):
        return "temp_serialize2XML"
    
    def get_ast(self,filename):
        debug = False
        safe_mode = False
        lexer = EzhilLex(filename,debug,encoding="UTF-8")
        parse_eval = EzhilInterpreter( lexer=lexer, debug=debug, safe_mode=safe_mode )
        parse_tree = parse_eval.parse()
        return parse_tree
    
    def test_basic(self):
        relpath  = "../../tests/"
        files = ["hello.n","ford2.n","adukku.n"]
        for file in files:
            parse_tree = self.get_ast(relpath+file)
            SerializerXML.serializeParseTree( parse_tree )
            
if __name__ == "__main__":
    unittest.main()
