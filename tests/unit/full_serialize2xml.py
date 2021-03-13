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
from ezhil.ezhil_program_utils import serializeSourceFile, serializeParseTree
from ezhil.ezhil_parser import ParseException

# helper functions for testsuites
import unittest
import codecs
import sys
import os
import traceback

import xml.parsers.expat


# Ref: http://code.activestate.com/recipes/65248-parsing-an-xml-file-with-xmlparsersexpat/
class XMLValidator:
    # prepare for parsing

    def __init__(self, xml_file):
        assert (xml_file != "")
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
            print(("ERROR: Can't open XML file -> %s.\n Casue: %s!\n" %
                  (self.xml_file, str(e))))
            raise e

    # TBD
    def handleCharData(self, data):
        pass

    def handleStartElement(self, name, attrs):
        pass

    def handleEndElement(self, name):
        pass


class SerializeToXML(unittest.TestCase):
    ref_path = ''

    def setUp(self):
        unittest.TestCase.setUp(self)
        cwd_path = os.path.abspath('./')
        _root1, _ = os.path.split(cwd_path)
        SerializeToXML.ref_path, _ = os.path.split(_root1)

    def get_filename(self):
        return "temp_serialize2XML"

    def run_basic_hook(self, posthook=None):
        relpath = os.path.join(SerializeToXML.ref_path, "tests", "")
        taboo = ["badlex.n", "nonexistent_file.n", "solo_return.n"]
        xml_taboo = [
        ]  #["bf0.n","boolean_demorgan.n","globalvars.n","boolean_fcns.n"]
        with codecs.open(os.path.join(SerializeToXML.ref_path, "test_cases"),
                         "r", "utf-8") as fp:
            files = []
            for f in fp.readlines():
                f = f.strip()
                if len(f) > 0 and not (f in taboo):
                    files.append(f)
        files.sort()
        for file in files:
            xmlfilename = relpath + file.replace(".n", ".xml")
            try:
                parse_tree = serializeSourceFile(srcfilename=relpath + file,
                                                 tgtfile=xmlfilename)
                if posthook and not (file in xml_taboo):
                    posthook(parse_tree, file, xmlfilename)
                os.unlink(xmlfilename)
                self.assertTrue(True, "Passed file #" + file)
                print(("## PASSED file #", file))
            #except ParseException as e:
            #    continue
            except Exception as e:
                print(("## FAILED file # ", file))
                traceback.print_exc()
                #print(unicode(e))

    def test_basic(self):
        self.run_basic_hook()

    def test_save_to_file(self):
        # 1. run same test as above but save contents to file
        # 2. next, run the XML validators to ensure well formed XML
        def xmlvalidation_hook(parse_tree, file, xmlfilename):
            #print("Validating XML file %s"%xmlfilename)
            try:
                XMLValidator(xmlfilename)
                self.assertTrue(True, "PASS - %s" % xmlfilename)
            except Exception as e:
                with open(xmlfilename, "r") as fp:
                    xmlcontents = fp.read()
                self.assertTrue(False, xmlcontents)

        self.run_basic_hook(posthook=xmlvalidation_hook)


if __name__ == "__main__":
    unittest.main()
