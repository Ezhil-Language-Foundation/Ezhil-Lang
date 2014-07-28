from django.shortcuts import render, render_to_response
from django.core.context_processors import csrf
from django.template import Context, RequestContext
from django.http import StreamingHttpResponse, HttpResponse

from ezhil import EzhilFileExecuter
import ezhil
import os, sys, tempfile, traceback, codecs

# Create your views here.

class EzhilWeb:
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

def evaluate( request ):
    progin = ''
    evaluated = False
    failed = False
    progout = ''
    exception = ''

    if request.method == "POST":
        vars = {}
        vars['eval'] = request.POST['eval']
        vars['prog'] = request.POST['prog']
        progin = vars['prog']

        try:
            evaluated = True
            # 10s timeout and executor
            obj = EzhilFileExecuter( file_input = [vars['prog']],
                                     redirectop =  True, TIMEOUT = 10 )
			
            # actually run the process
            obj.run()
			
            # get executed output in 'progout' and name of the two tmp files to cleanup
            [tmpfile,filename,progout] = obj.get_output()
            os.unlink( tmpfile )
            os.unlink( filename )
            
            if obj.exitcode != 0 and EzhilWeb.error_qualifiers(progout):
                failed = True
            else:
                failed = False
            
        except Exception as e:
            exception = str(e)
            failed = True
            [tmpfile,filename,progout] = obj.get_output()

            try:
                os.unlink( tmpfile )
            except Except as e:
                pass

            try:
                os.unlink( filename )
            except Except as e:
                pass
			
            #traceback.print_tb(sys.exc_info()[2])
            #raise e #debug mode
    
    ctx = Context({'evaluated_flag':evaluated,
                   'failed_flag':failed,
                   'program_input':progin,
                   'program_output':progout,
                   'exception_message':exception})
    
    return StreamingHttpResponse( render(request,"ezplay/eval.html", ctx ) )

def save( request, prefix ):
    return render_to_response("cannot save "+prefix+" at this moment")

def download( request, prefix ):
    return render_to_response("cannot download "+prefix+" at this moment")

def lookupp( request, prefix ):
    return render_to_response("cannot lookup "+prefix+" at this moment")
