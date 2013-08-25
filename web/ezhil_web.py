#!/usr/bin/python -u
# -*- coding: utf-8 -*-
## 
## (C) 2013 Muthiah Annamalai,
## Licensed under GPL Version 3
## 
## Ezhil language Interpreter via Web

## Ref: http://wiki.python.org/moin/BaseHttpServer

import time

import sys
from random import choice

# NB: this program imports Ezhil library from the installed version
from ezhil import EzhilFileExecuter #, EzhilInterpExecuter

#from os import unlink
import cgi

class EzhilWeb():
    """ Class that does the job on construction """
    def __init__(self,debug = False):
        self.debug = debug
        if ( self.debug ):
            # debugging tips
            import cgitb
            cgitb.enable()
        
        self.form = cgi.FieldStorage()
        try:
            program = self.form.getvalue('prog')
        except Exception as e:
            print "could not load the program from GET method"
        finally:
            if ( not program ):
                program = "printf(\"You can write Tamil programs from your browser!\")"
        
        if ( self.debug ):
            print(str(program))
    
        self.do_ezhil_execute( program )

    @staticmethod
    def get_image( kind ):
        if kind == 'success':
            img = choice(['trophy-gold','trophy-silver','trophy-bronze'])
        else:
            img = choice(['dialog-warning','software-update-urgent','stock_dialog-error'])
        img = img + '.png'
        return img
    
    @staticmethod
    def error_qualifiers( progout ):
        """ filter program execution output for Ezhil interpreter or Python stack traces"""
        FAILED_STRINGS = ["Traceback (most recent call last)",
                          "Run-time error Cannot Find Identifier"]
        return any(filter( lambda x: progout.find(x) > -1, FAILED_STRINGS))
    
    def do_ezhil_execute(self,program):
        # execute the Ezhil Interpreter with string @program
        print("<html> <head> <title>Ezhil interpreter</title> </head><body> ")
        program_fmt = """<TABLE>
        <TR><TD>
        <TABLE>
        <TR>
        <TD><font color=\"blue\"><OL>"""
        
        if ( self.debug ):
            print( "Source program <BR />" )
            print "program = ",program,"<BR />"
            print( "*"*60 )
            print("<BR />")
        
        program_fmt += "\n".join(["<li>%s</li>"%(prog_line)  for line_no,prog_line in enumerate(program.split('\n'))])
        program_fmt += """</OL></font></TD></TR>\n</TABLE></TD><TD>"""
        sys.stdout.flush()
        sys.stderr.flush()
        # run the interpreter in a sandbox and capture the output hopefully
        try:
            failed = False
            obj = EzhilFileExecuter( file_input = [program], redirectop = True, TIMEOUT = 60*2 ) # 2 minutes
            progout = obj.get_output()
            #SUCCESS_STRING = "<H2> Your program executed correctly! Congratulations. </H2>"            
            print obj.exitcode
            print progout
            if obj.exitcode != 0 and EzhilWeb.error_qualifiers(progout):
                if ( self.debug ):
                    print "Exitcode => ",obj.exitcode
                    print progout
                op = "<IMG SRC='../icons/%s' alt='failure' />"%EzhilWeb.get_image('failure')
                op = op + "%s <B>Failed Execution, with parsing or evaluation error</B> for program with <font color=\"red\">error <pre>%s</pre> </font></TD></TR></TABLE>"%(program_fmt,progout)
                failed = True
            else:
                failed = False
                op = "<IMG SRC='../icons/%s' alt='success' />"%EzhilWeb.get_image('success')
                op = op + "%s <B>Succeeded Execution</B> for program with output, <BR/> <font color=\"green\"><pre>%s</pre></font></TD></TR></TABLE>"%(program_fmt,progout)
        except Exception as e:
            if ( self.debug ):
                print "FAILED EXECUTION"
                print str(e)
            failed = True
            op = "<IMG SRC='../icons/%s' alt='failure' />"%EzhilWeb.get_image('failure')
            op = op + "%s <B>FAILED Execution</B> for program with <font color=\"red\">error <pre>%s</pre> </font></TD></TR></TABLE>"%(program_fmt,str(e)) 
        if ( self.debug ):
            print "Output file"
            print obj.get_output()
        
        prev_page = """<script>
    document.write("Navigate back to your source program : <a href='#' onClick='history.back();return false;'>Go Back</a>");
</script><BR />\n<HR/>\n"""
        print prev_page
        
        if failed:
            op = "<H2> Your program has some errors! Try correcting it and re-evaluate the code</H2><HR/><BR/>"+op
        else:
            op = "<H2> Your program executed correctly! Congratulations. </H2><HR/><BR/>"+op
        print op
        print("</body></html>\n")
 
        return op

if __name__ == '__main__':
    print("Content-Type: text/html")    # HTML is following
    print("")                              # blank line, end of headers
    # do the Ezhil thing    
    EzhilWeb(debug=False)
