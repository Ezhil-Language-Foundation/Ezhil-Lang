# -*- coding: utf-8 -*-
# (C) 2013 Muthiah Annamalai
# 
# This file is part of Ezhil Language test suite
# 

# setup the paths
import ezhiltests
from ezhiltests import TestEzhil

# helper functions for testsuites
import unittest
from test import test_support

from ezhil import PrettyPrint

class TestPrettyPrinter(unittest.TestCase):
    def test_run_addition(self):
        relpath  = "../../ezhil_tests/"

        hello_patterns = u"""<span style="color:#00FF00">exit</span><span style="color:#FF0000">)</span><BR />
<span style="color:#C0FFEE">"# இது ஒரு எழில் தமிழ் நிரலாக்க மொழி உதாரணம்"</span><BR />
<span style="color:#0000FF">பதிப்பி</span><span style="color:#CD5C5C">"இது என் முதல் எழில் நிரல்"</span><BR />"""

        fact_patterns = u"""<span style="color:#00FF00">ans</span><span style="color:#FF0000">=</span><span style="color:#00FF00">fact</span><span style="color:#FF0000">(</span><span style="color:#00FF00">ப</span><span style="color:#FF0000">-</span><span style="color:#FF8DC">4</span><span style="color:#FF0000">/</span><span style="color:#FF8DC">2</span><span style="color:#FF0000">)</span><BR />
<BR />
<span style="color:#0000FF">பதிப்பி</span><span style="color:#00FF00">ans</span>,<span style="color:#00FF00">assert</span><span style="color:#FF0000">(</span><span style="color:#00FF00">ans</span><span style="color:#FF0000">==</span><span style="color:#FF8DC">2</span><span style="color:#FF0000">)</span><BR />
<BR />
<span style="color:#00FF00">ans</span><span style="color:#FF0000">=</span><span style="color:#00FF00">fact</span><span style="color:#FF0000">(</span><span style="color:#FF8DC">0.75</span><span style="color:#FF0000">*</span><span style="color:#00FF00">ப</span><span style="color:#FF0000">-</span><span style="color:#FF8DC">4</span><span style="color:#FF0000">/</span><span style="color:#FF8DC">2</span><span style="color:#FF0000">)</span><BR />
<BR />"""
        file_patterns = {"hello.n" : hello_patterns.split("\n"),
                         "fact.n"  : fact_patterns.split("\n") }        
                
        flag = True
        
        for filename, expt_fmt in file_patterns.items():
            formatted_str = PrettyPrint(relpath+filename).pretty_print()
            if not ( all([( formatted_str.find( line ) >= 0 ) for line in expt_fmt]) ):
                print "file "+filename+" did not find expected strings "
                print u"\n>>>".join(expt_fmt)
                flag = False
            else:
                print "file " + filename + " passed the test"
        
        assert( flag )

if __name__ == '__main__':    
    test_support.run_unittest(TestPrettyPrinter)
