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
import sys
import os
import xml.parsers.expat

# Ref: http://code.activestate.com/recipes/65248-parsing-an-xml-file-with-xmlparsersexpat/
class XMLValidator:
    # prepare for parsing

    def __init__(self, xml_file):
        assert(xml_file != "")
        self.Parser = xml.parsers.expat.ParserCreate()
        self.xml_file = xml_file
        self.Parser.CharacterDataHandler = self.handleCharData
        self.Parser.StartElementHandler = self.handleStartElement
        self.Parser.EndElementHandler = self.handleEndElement
        self.parse()
    
    def parse(self):
        try:
            self.Parser.ParseFile(open(self.xml_file, "r"))
        except Exception as e:
            print("ERROR: Can't open XML file -> %s.\n Casue: %s!\n"%(self.xml_file,str(e)))
            raise e
        
    # TBD
    def handleCharData(self, data): pass
    def handleStartElement(self, name, attrs): pass
    def handleEndElement(self, name): pass

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
    
    def run_basic_hook(self,posthook=None):
        relpath  = "../../tests/"
        files = ["hello.n","ford2.n","adukku.n"]
        for file in files:
            parse_tree = self.get_ast(relpath+file)
            SerializerXML.serializeParseTree( parse_tree )
            if posthook:
                posthook(parse_tree,file)
            
    def test_basic(self):
        self.run_basic_hook()
        
    def test_save_to_file(self):
        # 1. run same test as above but save contents to file
        # 2. next, run the XML validators to ensure well formed XML
        def xmlvalidation_hook(parse_tree,file):
            xmlfilename = file.replace(".n",".xml")
            SerializerXML.serializeParseTree( parse_tree, filename=xmlfilename )    
            print("Validating XML file %s"%xmlfilename)
            try:
                XMLValidator(xmlfilename)
                self.assertTrue(True,"PASS - %s"%xmlfilename)
            except Exception as e:
                with open(xmlfilename,"r") as fp:
                    xmlcontents=fp.read()
                self.assertTrue(False,xmlcontents)
            os.unlink(xmlfilename)
        
        self.run_basic_hook(posthook=xmlvalidation_hook)
    
if __name__ == "__main__":
    unittest.main()
