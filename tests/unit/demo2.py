#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import ezhiltests, os

from ezhil import EzhilFileExecuter

import unittest
from test import test_support

import ezhil

program = u"""# மாதிரி =>  முடிவிலா சுழற்சி
# கூகிள் மொழிபெயர்ப்பு பயன்படுத்தி

i = 0
@( i < 100 ) வரை
 i = i + 11
#பதிப்பி "வணக்கம் >> ", i
முடி
"""

debug = False

class Executer(unittest.TestCase):
    def test_basic_file_settings(self):
        #print program
        obj = EzhilFileExecuter( file_input = [program], debug=True, redirectop = False, TIMEOUT = 10 ) # 2 minutes
        
        # actually run the process
        obj.run()
        
        # get executed output in 'progout' and name of the two tmp files to cleanup
        [tmpfile,filename,progout] = obj.get_output()
                
        if obj.exitcode != 0 and EzhilWeb.error_qualifiers(progout):
            failed = True
        else:
            failed = False
        
        if ( debug ):
            print (u"output = ")
            print (u"%s,%s"%(progout.decode('utf-8'), str(failed)))
        return

    def test_basic_file_settings_no_redirect(self):
        #print program
        obj = EzhilFileExecuter( file_input = [program], debug=False, redirectop = False, TIMEOUT = 10 ) # 2 minutes
        
        # actually run the process
        obj.run()

        # get executed output in 'progout' and name of the two tmp files to cleanup
        [tmpfile,filename,progout] = obj.get_output()

        #os.unlink( tmpfile )
        #os.unlink( filename )
        
        if obj.exitcode != 0 and EzhilWeb.error_qualifiers(progout):
            failed = True
        else:
            failed = False

        if ( debug ):
            print (u"output = ")
            print (u"%s,%s"%(progout.decode('utf-8'), str(failed)))        
        return

if __name__ == '__main__':    
    unittest.main()
