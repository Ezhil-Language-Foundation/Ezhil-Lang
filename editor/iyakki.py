#!/usr/bin/env python
##This Python file uses the following encoding: utf-8
##
## (C) 2016-2017 Muthiah Annamalai,
## Licensed under GPL Version 3
## Certain sections of code are borrowed from public sources and are attributed accordingly.

from __future__ import print_function

import codecs
import multiprocessing
import os
import re
import sys
import tempfile
import threading
import time

import gi
import ezhil

PYTHON3 = (sys.version[0] == '3')
if PYTHON3:
    unicode = str

gi.require_version('Gtk','3.0')

from gi.repository import Gtk, GObject, GLib, Pango

def MPRunner_actor(pipe,filename):
    multiprocessing.freeze_support()
    GObject.threads_init()
    is_success = False
    ezhil.EzhilCustomFunction.set(GtkStaticWindow.dummy_input)
    old_stdin = sys.stdin
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    tmpfilename = tempfile.mktemp()+".n"
    res_std_out = u""
    old_exit = sys.exit
    sys.exit = lambda x: 0
    try:
        sys.stdout = codecs.open(tmpfilename,"w","utf-8")
        sys.stderr = sys.stdout
        executer = ezhil.EzhilFileExecuter(filename)
        executer.run()
        is_success = True
    except Exception as e:
        print(u" '{0}':\n{1}'".format(filename, unicode(e)))
    finally:
        print(u"######- நிரல் இயக்கி முடிந்தது-######")
        sys.exit = old_exit
        sys.stdout.flush()
        sys.stdout.close()
        with codecs.open(tmpfilename,u"r",u"utf-8") as fp:
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
        self.res_std_out = u""
    
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
            res_std_out = u"இயக்கும் நேரம் %g(s) வினாடிகள் முடிந்தது காலாவதி ஆகியது\n"%self.timeout
        else:
            is_success = False
            res_std_out = u"தெரியாத பிழை நேர்ந்தது!"
        self.res_std_out,self.is_success = res_std_out,is_success
        return

class GtkStaticWindow:
    _instance = None

    @staticmethod
    def get_instance():
        if not GtkStaticWindow._instance:
            GtkStaticWindow._instance = GtkStaticWindow()
        return GtkStaticWindow._instance

    def __init__(self):
        self.gui = threading.Thread(target=lambda : Gtk.main_iteration())
        
        self.window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        self.window.set_default_size(100,150) #vanishingly small size
        self.window.connect("delete-event",Gtk.main_quit)
        self.window.set_title(u"எழில் இயக்கி சாளரம்")
        self.window.set_decorated(False)
        self.window.show_all()
        GLib.idle_add( Gtk.main_iteration )
        self.gui.start()

    @staticmethod
    def dummy_input(*args):
        message= not args and "Enter Input" or args[0]
        if not args or len(args) < 2:
            title = u"எழுதி - எழில் மொழி செயலி" #Ezhil language IDE
        else:
            title = args[1]
        static_window = GtkStaticWindow.get_instance()
        window = static_window.window
        dialogWindow = Gtk.MessageDialog(window,
                              Gtk.DialogFlags.MODAL,
                              Gtk.MessageType.QUESTION,
                              Gtk.ButtonsType.OK_CANCEL,
                              message)
        dialogWindow.set_title(title)
        dialogBox = dialogWindow.get_content_area()
        userEntry = Gtk.Entry()
        userEntry.set_size_request(257,0)
        dialogBox.pack_end(userEntry, False, False, 0)
        dialogWindow.show_all()
        response = dialogWindow.run()
        text = userEntry.get_text() 
        print(u"#####- உள்ளீடு நிரல்பாகம் இயங்கி முடிந்தது -####")
        if (response == Gtk.ResponseType.OK) and (text != ''):
            return text
        return ""

if __name__ == "__main__":
    filename = sys.argv[1]
    runner = MPRunner()
    runner.run(filename)
