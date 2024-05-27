#!/usr/bin/env python
##This Python file uses the following encoding: utf-8
##
## (C) 2016-2017 Muthiah Annamalai,
## Licensed under GPL Version 3
## Certain sections of code are borrowed from public sources and are attributed accordingly.



import codecs
import multiprocessing
import os
import re
import sys
import tempfile
import threading
import time

import ezhil

PYTHON3 = (sys.version[0] == '3')
if PYTHON3:
    str = str

def MPRunner_actor(pipe,filename):
    multiprocessing.freeze_support()
    is_success = False
    old_stdin = sys.stdin
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    tmpfilename = tempfile.mktemp()+".n"
    res_std_out = ""
    old_exit = sys.exit
    sys.exit = lambda x: 0
    try:
        sys.stdout = codecs.open(tmpfilename,"w","utf-8")
        sys.stderr = sys.stdout
        executer = ezhil.EzhilFileExecuter(filename,debug=False,redirectop=False,TIMEOUT=3,encoding="utf-8",doprofile=False,safe_mode=True)
        executer.run()
        is_success = True
    except Exception as e:
        print(" '{0}':\n{1}'".format(filename, str(e)))
    finally:
        print("######- நிரல் இயக்கி முடிந்தது-######")
        sys.exit = old_exit
        sys.stdout.flush()
        sys.stdout.close()
        with codecs.open(tmpfilename,"r","utf-8") as fp:
            res_std_out = fp.read()
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        sys.stdin = old_stdin
    #print(pipe)
    #print("sending data back to source via pipe")
    pipe.send([ res_std_out,is_success] )
    pipe.close()

class MPRunner:
    is_success = False
    def __init__(self,timeout=60,autorun=False):
        self.timeout = min(timeout,autorun and 5 or timeout)
        self.is_success = False
        self.res_std_out = ""
    
    def run(self,filename):
        # Start bar as a process
        parent_conn, child_conn = multiprocessing.Pipe()
        p = multiprocessing.Process(target=MPRunner_actor,args=([child_conn,filename]))
        p.start()
        child_conn.close()
        if parent_conn.poll(self.timeout):
            res_std_out, is_success = parent_conn.recv()
            p.join(0)
            parent_conn.close()
        elif p.is_alive():
            p.terminate()
            p.join()
            is_success = False
            res_std_out = "இயக்கும் நேரம் %g(s) வினாடிகள் முடிந்தது காலாவதி ஆகியது\n"%self.timeout
        else:
            is_success = False
            res_std_out = "தெரியாத பிழை நேர்ந்தது!"
        self.res_std_out,self.is_success = res_std_out,is_success
        return
        
    def __str__(self):
        r = list()
        if self.is_success:
            r.append("SUCCESS")
        else:
            r.append("FAILURE")
            
        r.append("\nOUTPUT:")
        r.append(self.res_std_out)
        return " ".join(r)
        
    def report(self):
        if self.is_success:
            print("SUCCESS")
        else:
            print("FAILURE")
            
        print("OUTPUT:")
        print(self.res_std_out)

if __name__ == "__main__":
    filename = sys.argv[1]
    runner = MPRunner()
    runner.run(filename)
    runner.report()
