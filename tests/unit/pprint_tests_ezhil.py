
# -*- coding: utf-8 -*-
# (C) 2013 Muthiah Annamalai
# 
# This file is part of Ezhil Language test suite
# 

# setup the paths
import ezhiltests
from ezhiltests import TestEzhil, QuietTestCase

# helper functions for testsuites
import sys
import os
import codecs
import unittest
from test import test_support

from ezhil import PrettyPrint

debug = False

class TestPrettyPrinter(QuietTestCase):
    def get_filename(self):
        return 'dummy_TestPrettyPrinter.txt'
    
    def test_run_addition(self):
        relpath  = "../../tests/"

        hello_patterns = u"""<span style="color:#00FF00">exit</span><span style="color:#FF0000">)</span><BR />
<span style="color:#C0FFEE">"# இது ஒரு எழில் தமிழ் நிரலாக்க மொழி உதாரணம்"</span><BR />
<span style="color:#0000FF">பதிப்பி</span><span style="color:#CD5C5C">"இது என் முதல் எழில் நிரல்"</span><BR />"""

        fact_patterns = u"""
<span style="color:#0000FF">நிரல்பாகம்</span><span style="color:#00FF00">fact</span><span style="color:#FF0000">( </span><span style="color:#00FF00">n</span><span style="color:#FF0000">) </span><span style="color:#FF0000">@( </span><BR />
<span style="color:#00FF00">n</span><span style="color:#FF0000">==</span><span style="color:#FF8DC">0</span><span style="color:#FF0000">) </span><span style="color:#0000FF">ஆனால்</span><BR />
<span style="color:#0000FF">பின்கொடு</span><span style="color:#FF8DC">1</span><BR />
<BR />
<span style="color:#0000FF">முடி</span><BR />
<BR />
<BR />
<span style="color:#0000FF">பதிப்பி</span><span style="color:#00FF00">fact</span><span style="color:#FF0000">(</span><span style="color:#FF8DC">10</span><span style="color:#FF0000">)</span><BR />
<BR />
<span style="color:#00FF00">ப</span><span style="color:#FF0000">=</span><span style="color:#FF8DC">4</span><BR />
<BR />
<span style="color:#00FF00">ans</span><span style="color:#FF0000">=</span><span style="color:#00FF00">fact</span><span style="color:#FF0000">(</span><span style="color:#00FF00">ப</span><span style="color:#FF0000">+</span><span style="color:#FF8DC">4</span><span style="color:#FF0000">)</span><BR />
<BR />
<span style="color:#00FF00">ans</span><span style="color:#FF0000">=</span><span style="color:#00FF00">fact</span><span style="color:#FF0000">(</span><span style="color:#00FF00">ப</span><span style="color:#FF0000">-</span><span style="color:#FF8DC">4</span><span style="color:#FF0000">/</span><span style="color:#FF8DC">2</span><span style="color:#FF0000">)</span><BR />
<BR />
<span style="color:#0000FF">பதிப்பி</span><span style="color:#00FF00">ans</span>,<span style="color:#00FF00">assert</span><span style="color:#FF0000">(</span><span style="color:#00FF00">ans</span><span style="color:#FF0000">==</span><span style="color:#FF8DC">2</span><span style="color:#FF0000">)</span><BR />
<BR />
<span style="color:#00FF00">ans</span><span style="color:#FF0000">=</span><span style="color:#00FF00">fact</span><span style="color:#FF0000">(</span><span style="color:#FF8DC">0.75</span><span style="color:#FF0000">*</span><span style="color:#00FF00">ப</span><span style="color:#FF0000">-</span><span style="color:#FF8DC">4</span><span style="color:#FF0000">/</span><span style="color:#FF8DC">2</span><span style="color:#FF0000">)</span><BR />
<BR />"""

        infinite_loop_patterns = u"""
<span style="color:#00FF00">i</span><span style="color:#FF0000">>=</span><span style="color:#FF8DC">0</span><span style="color:#FF0000">) </span><span style="color:#0000FF">வரை</span><BR />
<span style="color:#00FF00">i</span><span style="color:#FF0000">=</span><span style="color:#00FF00">i</span><span style="color:#FF0000">+</span><span style="color:#FF8DC">1</span><BR />
<span style="color:#0000FF">முடி</span><BR />
"""

        ford2_patterns = u"""
<span style="color:#FF0000">@( </span><BR />
<span style="color:#00FF00">x</span><span style="color:#FF0000">=</span><span style="color:#FF8DC">0</span><span style="color:#FF0000">-</span><span style="color:#FF8DC">1</span><span style="color:#FF0000">, </span><span style="color:#FF8DC">0</span><span style="color:#FF0000">, </span><span style="color:#FF8DC">0</span><span style="color:#FF0000">) </span><span style="color:#0000FF">ஆக</span><BR />
<span style="color:#0000FF">பதிப்பி</span><span style="color:#00FF00">x</span>,<span style="color:#CD5C5C">"கருவேபில"</span><BR />
<BR />
#without this stmt it is a infinite loop<BR />
<span style="color:#0000FF">நிறுத்து</span><BR />
<BR />
<span style="color:#0000FF">முடி</span><BR />
<BR />
<span style="color:#00FF00">assert</span><span style="color:#FF0000">(</span><span style="color:#00FF00">x</span><span style="color:#FF0000">==</span><span style="color:#FF8DC">0</span><span style="color:#FF0000">-</span><span style="color:#FF8DC">1</span><span style="color:#FF0000">)</span><BR />
<span style="color:#FF0000">@( </span><BR />
<span style="color:#00FF00">x</span><span style="color:#FF0000">=</span><span style="color:#FF8DC">0</span><span style="color:#FF0000">-</span><span style="color:#FF8DC">1</span><span style="color:#FF0000">, </span><span style="color:#00FF00">x</span><span style="color:#FF0000"><</span><span style="color:#FF8DC">0</span><span style="color:#FF0000">, </span><span style="color:#00FF00">x</span><span style="color:#FF0000">=</span><span style="color:#00FF00">x</span><span style="color:#FF0000">+</span><span style="color:#FF8DC">1</span><span style="color:#FF0000">) </span><span style="color:#0000FF">ஆக</span><BR />
<span style="color:#0000FF">பதிப்பி</span><span style="color:#00FF00">x</span>,<span style="color:#CD5C5C">"கருவேபில"</span><BR />
<span style="color:#0000FF">முடி</span><BR />

"""

        file_patterns = {"hello.n" : hello_patterns,
                         "fact.n"  : fact_patterns, #check for fcn declarations as well
                         "infinite_loop.n" : infinite_loop_patterns,
                         "ford2.n" : ford2_patterns,                         
                        }
                
        flag = True
        for filename, expt_fmt in file_patterns.items():
            expt_fmt = expt_fmt.split("\n");
            formatted_str = PrettyPrint(relpath+filename).pretty_print()
            if not ( all([( formatted_str.find( line ) >= 0 ) for line in expt_fmt]) ):
                if debug: print "file "+filename+" did not find expected strings "
                if debug: print u"\n>>>".join(expt_fmt)
                flag = False
            else:
                if debug: print "file " + filename + " passed the test"
        
        self.assertTrue( flag )

if __name__ == '__main__':    
    test_support.run_unittest(TestPrettyPrinter)
