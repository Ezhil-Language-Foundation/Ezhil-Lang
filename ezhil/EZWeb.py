#!/usr/bin/python
# -*- coding: utf-8 -*-
## 
## (C) 2013 Muthiah Annamalai,
## Licensed under GPL Version 3
## 
## Interpreter for Ezhil language on the web

## Ref: http://wiki.python.org/moin/BaseHttpServer

import time
from ezhil import EzhilFileExecuter, EzhilInterpExecuter
import BaseHTTPServer, tempfile, threading
from SimpleHTTPServer import SimpleHTTPRequestHandler
from SocketServer import ThreadingMixIn
from os import unlink
import cgi

class BaseEzhilOnTheWeb(SimpleHTTPRequestHandler):
    def do_GET(self):        
        print(str(self.headers), "in thread =", threading.currentThread().getName())

        if self.path.find('/ezhil') >= 0:
            GETvars = cgi.parse_qs( self.path )
            print str(GETvars)
            if GETvars.has_key('prog'):
                program = "\n".join(GETvars['prog'])
            elif GETvars.has_key('eval'):
                program = 'printf("Welcome to Ezhil! You can type a program and see its output here!")\n'
            else:                
                # delegate upward
                SimpleHTTPRequestHandler.do_GET(self)
                return
            self.send_response(200)
            self.send_header("Content-type", "text/html")            
            self.end_headers()
            self.do_ezhil_execute( program )
        else:
            #delegate to parent
            SimpleHTTPRequestHandler.do_GET(self)
        return
    
    def do_ezhil_execute(self,program):
        # write the input program into a temporary file and execute the Ezhil Interpreter
        tmpf=tempfile.NamedTemporaryFile(suffix='.n',delete=False)
        tmpf.write(program)
        tmpf.close()
        
        print( "Source program" )
        print( open(tmpf.name).read() )
        print( "*"*60 )
        
        program_fmt = "\n".join(["<li>%s</li>"%(prog_line)  for line_no,prog_line in enumerate(program.split('\n'))]);

        # run the interpreter in a sandbox and capture the output hopefully
        try:
            failed = False
            obj = EzhilFileExecuter( file_input = tmpf.name, redirectop = True )
            #obj = EzhilInterpExecuter( file_input = tmpf.name, redirectop = True )
            progout = obj.get_output()            
            op = "<B>Succeeded Execution</B> for program <font color=\"blue\"><ol>%s</ol></font> as <br/> <font color=\"green\"><pre>%s</pre></font>"%(program_fmt,progout)
        except Exception as e:
            print str(e)
            failed = True
            op = "<B>FAILED Execution</B> for program <font color=\"blue\"><ol>%s</ol></font> with <font color=\"red\">error <pre>%s</pre> </font>"%(program_fmt,str(e))
        else:
            print "Output file"
            obj.get_output()
        
        # delete the temporary file
	try:
            unlink(tmpf.name)
        except Exception as e:
            print("Exception %s but we pass it"%str(e))
        
        prev_page = """<script>
    document.write("Navigate back to your source program : <a href='#' onClick='history.back();return false;'>Go Back</a>");
</script><HR/>"""
        #op = ""
        if failed:
            op = "<H2> Your program has some errors! Try correcting it and re-evaluate the code</H2><HR/><BR/>"+op
        else:
            op = "<H2> Your program executed correctly! Congratulations. </H2><HR/><BR/>"+op            
        op = prev_page + op
        self.wfile.write("<html> <head> <title>Ezhil interpreter</title> </head><body> %s </body></html>\n"%op)
        
        return op

class EzhilOnTheWeb(ThreadingMixIn,BaseEzhilOnTheWeb):
    """ Add threading to handle requests in separate thread """

HOST_NAME = "localhost"
PORT_NUMBER = 8080

if __name__ == "__main__":
    httpd = BaseHTTPServer.HTTPServer((HOST_NAME, PORT_NUMBER), EzhilOnTheWeb)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
