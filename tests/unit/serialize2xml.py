# -*- coding: utf-8 -*-
# (C) 2015 Muthiah Annamalai
# 
# This file is part of Ezhil Language test suite
# 

# setup the paths
import ezhiltests
import codecs
from ezhiltests import TestEzhilException, QuietTestCase, ezhil
from ezhil import EzhilInterpreter, EzhilLex
from ezhil.ezhil_serializer import SerializerXML
from ezhil.ezhil_program_utils import serializeSourceFile, serializeParseTree

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
        #try:
        class ShimObj:
            def __init__(self,that):
                self._file = codecs.open(that.xml_file, "rb", "utf-8")
                self._offset = 0
                self._data = bytes(self._file.read(),'utf-8')

            def read(self,size):
                data = self._data[self._offset:min(len(self._data),self._offset+size)]
                self._offset += size
                return data

        self.Parser.ParseFile(ShimObj(self))
        #except Exception as e:
        #    print("ERROR: Can't open XML file -> %s.\n Cause: %s!\n"%(self.xml_file,str(e)))
        #    raise e
        
    # TBD
    def handleCharData(self, data): pass
    def handleStartElement(self, name, attrs): pass
    def handleEndElement(self, name): pass

class SerializeToXML(QuietTestCase):
    def get_filename(self):
        return "temp_serialize2XML"

    def run_basic_hook(self,posthook=None):
        relpath  = "../../tests/"
        files = ["hello.n","ford2.n","adukku.n"]
        for file in files:
            xmlfilename = relpath+file.replace(".n",".xml")
            parse_tree = serializeSourceFile( srcfilename = relpath+file,tgtfile = xmlfilename )
            if posthook:
                posthook(parse_tree,file,xmlfilename)
            os.unlink(xmlfilename)

    def test_basic(self):
        self.run_basic_hook()
        
    def test_save_to_file(self):
        # 1. run same test as above but save contents to file
        # 2. next, run the XML validators to ensure well formed XML
        def xmlvalidation_hook(parse_tree,file,xmlfilename):
            print("Validating XML file %s"%xmlfilename)
            try:
                XMLValidator(xmlfilename)
                self.assertTrue(True,"PASS - %s"%xmlfilename)
            except Exception as e:
                with open(xmlfilename,"r") as fp:
                    xmlcontents=fp.read()
                self.assertTrue(False,xmlcontents)
        
        self.run_basic_hook(posthook=xmlvalidation_hook)
    
if __name__ == "__main__":
    unittest.main()
