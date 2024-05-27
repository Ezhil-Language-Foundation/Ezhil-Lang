#!/usr/bin/python -u
# -*- coding: utf-8 -*-
## 
## (C) 2013-2015 Muthiah Annamalai,
## Licensed under GPL Version 3
## 
## Ezhil language Interpreter via Web

## Ref: http://wiki.python.org/moin/BaseHttpServer

import time

import sys, os
from random import choice

# NB: this program imports Ezhil library from the installed version
from ezhil import EzhilFileExecuter #, EzhilInterpExecuter

#from os import unlink
import cgi

import urllib.request, urllib.parse, urllib.error
import re

class EzhilWeb():
    """ Class that does the job on construction """
    def __init__(self,debug = False):
        self.debug = debug
        self.img_outcome = '' #image str indicating success/failure
        if ( self.debug ):
            # debugging tips
            import cgitb
            cgitb.enable()
        
        self.form = cgi.FieldStorage()
        try:
            program = self.form.getvalue('prog')
        except Exception as e:
            print("could not load the program from GET method, exception ",str(e))
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
        return any([x for x in FAILED_STRINGS if progout.find(x) > -1])
    
    def do_ezhil_execute(self,program):
        # execute the Ezhil Interpreter with string @program
        print("<html> <head> <title>Ezhil interpreter</title>")
        print("""<script src="./Blob.js"></script>
<script src="./FileSaver.js"></script>
<script lang="text/javascript">
  function download(filename, content) {
    saveAs( new Blob([content],{type: "application/x-ezhil;charset=utf-8"}), filename);
  }
</script>""")
        print("</head><body> ")
        print("<!-- ") #suppress exec stdout
        close_comment = False #and useful to debug a live site
        program_fmt = """<TABLE>
        <TR><TD>
        <TABLE>
        <TR>
        <TD><font color=\"blue\"><OL>"""
        
        if ( self.debug ):
            print( "Source program <BR />" )
            print("program = ",program,"<BR />")
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
            obj.run()

            [f1,f2,progout] = obj.get_output()
            for f in [f1,f2]:
                try:
                    os.unlink( f )
                except Exception as e:
                    pass
            
        
            #SUCCESS_STRING = "<H2> Your program executed correctly! Congratulations. </H2>"            
            if ( self.debug ):
                print(obj.exitcode)
                print(progout)
            print("-->")
            close_comment = True
            if obj.exitcode != 0 and EzhilWeb.error_qualifiers(progout):
                if ( self.debug ):
                    print("Exitcode => ",obj.exitcode)
                    print(progout)
                self.img_outcome = "<IMG width='64' SRC='../icons/%s' alt='failure' />"%EzhilWeb.get_image('failure')
                op = "%s <B>%s Failed Execution, with parsing or evaluation error</B> for program with <font color=\"red\">error <pre>%s</pre> </font></TD></TR></TABLE>"%(program_fmt,self.img_outcome,progout)
                failed = True
            else:
                failed = False
                self.img_outcome = "<IMG width='64' SRC='../icons/%s' alt='success' />"%EzhilWeb.get_image('success')
                op = "%s <B>%s Succeeded Execution</B> for program with output, <BR/> <font color=\"green\"><pre>%s</pre></font></TD></TR>"%(program_fmt,self.img_outcome,progout)
                op = op + saveYourCode(program)
                op = op + "</TABLE>"
        except Exception as e:
            raise e
            if( not close_comment ):
                print("-->")
            if ( self.debug ):
                print("FAILED EXECUTION")
                print(str(e))
            failed = True
            self.img_outcome = "<IMG SRC='../icons/%s' width='64' alt='failure' />"%EzhilWeb.get_image('failure')
            op = "%s <B>%s FAILED Execution</B> for program with <font color=\"red\">error <pre>%s</pre> </font></TD></TR>"%(program_fmt,self.img_outcome,str(e)) 
            op = op + saveYourCode(program)
            op = op + "</TABLE>"
        if ( self.debug ):
            print("Output file")
            print(obj.get_output())
        prev_page = "<script>\ndocument.write(\"Navigate back to your source program : <a href='#' onClick='history.back();return false;'>Go Back</a>\");\n</script><BR />\n<HR/>\n"
        print(prev_page)
        #op = self.img_outcome + op        
        if failed:
            op = "<H2> Your program has some errors! Try correcting it and re-evaluate the code</H2><HR/><BR/>"+op
        else:
            op = "<H2> Your program executed correctly! Congratulations. </H2><HR/><BR/>"+op
        print(op.decode("utf-8"))
        print("</body></html>\n")
 
        return op

def saveYourCode( program ):
    tprefix = time.ctime().replace(' ','_').replace(':','_')
    return """<TR><TD>
<a  href="javascript:download('"""+"ezhil_program_"+tprefix+".n','"+program.replace('\n','\\n').replace('"','\"').replace(">","&gt;").replace("<","&lt;")+"""')">உங்கள் நிரலை சேமிக்க (save your code)</a></TD></TR>"""

if __name__ == '__main__':
    print("Content-Type: text/html")    # HTML is following
    print("")                              # blank line, end of headers
    # do the Ezhil thing
    EzhilWeb(debug=False)
