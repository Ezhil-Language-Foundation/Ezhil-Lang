#!/usr/bin/python
# -*- coding: utf-8 -*-
## 
## (C) 2013 Muthiah Annamalai,
## Licensed under GPL Version 3
## 
## Ezhil language Interpreter via Web

## Ref: http://wiki.python.org/moin/BaseHttpServer

import time
from ezhil import EzhilFileExecuter, EzhilInterpExecuter
import BaseHTTPServer, tempfile, threading
from SimpleHTTPServer import SimpleHTTPRequestHandler
from SocketServer import ThreadingMixIn
from CGIHTTPServer import CGIHTTPRequestHandler
from os import unlink
import cgi, cgitb, codecs
import sys, traceback

cgitb.enable()

DEBUG=False

class BaseEzhilWeb(SimpleHTTPRequestHandler):    
    def do_GET(self):
        print(str(self.headers), "in thread =", threading.currentThread().getName())    
        #delegate to parent
        SimpleHTTPRequestHandler.do_GET(self)
        return
    
    def do_POST(self):
        query_string = self.rfile.read(int(self.headers['Content-Length']))
        print query_string
        POSTvars = cgi.parse_qs( query_string )
        print str(POSTvars)
        
        if POSTvars.has_key('prog'):
            program ="\n".join(POSTvars['prog'])
            program = codecs.decode( program ,'utf-8')
        elif POSTvars.has_key('eval'):
            program = 'printf("Welcome to Ezhil! You can type a program and execute it online!")'
        else:
            self.send_response(404)
            self.send_header("Content-type","text/html")
            self.end_headers()
            self.wfile.write( "<h1>HTTP 404 : Error occured</h1>" )
            self.wfile.write( str(POSTvars) )
            return
        
        self.send_response(200)
        self.send_header("Content-type","text/html; charset=utf-8")
        self.end_headers()
        self.do_ezhil_execute( program )        
        
        return
    
    def do_ezhil_execute(self,program):
        # write the input program into a temporary file and execute the Ezhil Interpreter
        
        program_fmt = u"""<TABLE>
        <TR><TD>
        <TABLE>
        <TR>
        <TD><font color=\"blue\"><OL>"""
        
        print( u"Source program" )
        print( program )
        print( u"*"*60 )
        
        program_fmt += u"\n".join(["<li>%s</li>"%(prog_line)  for line_no,prog_line in enumerate(program.split('\n'))])
        program_fmt += u"""</OL></font></TD></TR>\n</TABLE></TD><TD>"""
        
        # run the interpreter in a sandbox and capture the output hopefully
        try:
            failed = True #default failed mode
            obj = EzhilFileExecuter( file_input = [program], redirectop = True, TIMEOUT = 60*2 ) # 2 minutes
            
            # actually run the process
            obj.run()
        
            # get executed output in 'progout' and name of the two tmp files to cleanup
            [tmpfile,filename,progout] = obj.get_output()
            
            for f in [tmpfile,filename]:
                try:
                    os.unlink( f )
                except Exception as e:
                    pass
                
            if obj.exitcode != 0: #and EzhilWeb.error_qualifiers(progout)
                failed = True
            else:
                failed = False

            # output from ezhil interpreter is in form of UTF-8 strings, we extract
            # it from ASCII format I/O since we are in CGI mode.
            progout = progout.decode('utf-8')
            if DEBUG:
                print u"output = "
                print progout
            
            #SUCCESS_STRING = "<H2> Your program executed correctly! Congratulations. </H2>"
            FAILED_STRING = "Traceback (most recent call last)"
            if obj.exitcode != 0 and progout.find(FAILED_STRING) > -1:
                print u"Exitcode => ",obj.exitcode
                op = u"%s <B>FAILED Execution, with parsing or evaluation error</B> for program with <font color=\"red\">error <pre>%s</pre> </font></TD></TR></TABLE>"%(program_fmt,progout)
            else:
                failed = False
                obj.exitcode = 0
                op = u"%s <B>Succeeded Execution</B> for program with output, <BR/> <font color=\"green\"><pre>%s</pre></font></TD></TR></TABLE>"%(program_fmt,progout)
        except Exception as e:
            print u"FAILED EXECUTION"
            print str(e)
            traceback.print_tb(sys.exc_info()[2])
            failed = True
            op = u"%s <B>FAILED Execution</B> for program with <font color=\"red\">error <pre>%s</pre> </font></TD></TR></TABLE>"%(program_fmt,str(e))
        else:
            print u"Output file"
            obj.get_output()
        
        prev_page = u"""<script>
    document.write("Navigate back to your source program : <a href='#' onClick='history.back();return false;'>Go Back</a>");
</script><HR/>"""
        #op = ""
        if failed:
            op = u"<H2> Your program has some errors! Try correcting it and re-evaluate the code</H2><HR/><BR/>"+op
        else:
            op = u"<H2> Your program executed correctly! Congratulations. </H2><HR/><BR/>"+op            
        op = prev_page + op
        real_op = u"<html> <head> <title>Ezhil interpreter</title> </head><body> %s </body></html>\n"%op
        
        # CGI pipe only allows ASCII style strings
        self.wfile.write(real_op.encode('utf-8'))
        
        return op

class EzhilWeb(ThreadingMixIn,BaseEzhilWeb):
    """ Add threading to handle requests in separate thread """
    pass

HOST_NAME = "localhost"
PORT_NUMBER = 8080

if __name__ == "__main__":
    httpd = BaseHTTPServer.HTTPServer((HOST_NAME, PORT_NUMBER), EzhilWeb)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
