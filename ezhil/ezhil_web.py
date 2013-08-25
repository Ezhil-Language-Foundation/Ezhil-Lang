#!/usr/bin/python
# -*- coding: utf-8 -*-
## 
## (C) 2013 Muthiah Annamalai,
## Licensed under GPL Version 3
## 
## Ezhil language Interpreter via Web

## Ref: http://wiki.python.org/moin/BaseHttpServer

import tempfile
import time
from ezhil import EzhilFileExecuter, EzhilInterpExecuter
from os import unlink
import cgi

# debugging tips
import cgitb
cgitb.enable()

class EzhilWeb():
    """ Class that does the job on construction """
    def __init__(self,debug = False):
	self.debug =debug
	self.form = cgi.FieldStorage()
	try:
		program = self.form.getvalue('prog')
	except Exception as e:
		print "could not load the program from GET method"
		program = "print(\"You can write Tamil programs from your browser!\")"
	
	if ( self.debug ):
	        print(str(program))
   	self.do_ezhil_execute( program )
    
    def do_ezhil_execute(self,program):
        # write the input program into a temporary file and execute the Ezhil Interpreter
        tmpf=tempfile.NamedTemporaryFile(suffix='.n',delete=False)
	print "program = ",program
        tmpf.write(program)
        tmpf.close()
		
        program_fmt = """<TABLE>
		<TR><TD>
		<TABLE>
		<TR>
		<TD><font color=\"blue\"><OL>"""
		
        print( "Source program" )
        print( open(tmpf.name).read() )
        print( "*"*60 )
        
        program_fmt += "\n".join(["<li>%s</li>"%(prog_line)  for line_no,prog_line in enumerate(program.split('\n'))])
        program_fmt += """</OL></font></TD></TR>\n</TABLE></TD><TD>"""
		
        # run the interpreter in a sandbox and capture the output hopefully
        try:
            failed = False
            obj = EzhilFileExecuter( file_input = tmpf.name, redirectop = False, TIMEOUT = 60*2 ) # 2 minutes
            #obj = EzhilInterpExecuter( file_input = tmpf.name, redirectop = True )
            progout = obj.get_output()            
            if obj.exitcode != 0 :                
                op = "%s <B>FAILED Execution, with parsing or evaluation error</B> for program with <font color=\"red\">error <pre>%s</pre> </font></TD></TR></TABLE>"%(program_fmt,progout)
            else:
                op = "%s <B>Succeeded Execution</B> for program with output, <BR/> <font color=\"green\"><pre>%s</pre></font></TD></TR></TABLE>"%(program_fmt,progout)
        except Exception as e:
            print "FAILED EXECUTION"
            print str(e)
            failed = True
            op = "%s <B>FAILED Execution</B> for program with <font color=\"red\">error <pre>%s</pre> </font></TD></TR></TABLE>"%(program_fmt,str(e))
        else:
            print "Output file"
            obj.get_output()
        
#        # delete the temporary file
#	try:
#            unlink(tmpf.name)
#        except Exception as e:
#            print("Exception %s but we pass it"%str(e))
        
        prev_page = """<script>
    document.write("Navigate back to your source program : <a href='#' onClick='history.back();return false;'>Go Back</a>");
</script><HR/>"""
        #op = ""
        if failed:
            op = "<H2> Your program has some errors! Try correcting it and re-evaluate the code</H2><HR/><BR/>"+op
        else:
            op = "<H2> Your program executed correctly! Congratulations. </H2><HR/><BR/>"+op            
        op = prev_page + op
        print("<html> <head> <title>Ezhil interpreter</title> </head><body> %s </body></html>\n"%op)
 
        # delete the temporary file
        try:
            unlink(tmpf.name)
        except Exception as e:
            print("Exception %s but we pass it"%str(e))
       
        return op

if __name__ == '__main__':
	print("Content-Type: text/html")    # HTML is following
	print("")                              # blank line, end of headers
	# do the Ezhil thing	
	EzhilWeb(debug=True)

