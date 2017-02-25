#!/usr/bin/env python
##This Python file uses the following encoding: utf-8
##
## (C) 2016 Muthiah Annamalai,
## Licensed under GPL Version 3
##
from __future__ import print_function
import codecs
import sys
import os
try:
    import envoy
except ImportError as ie:
    pass
import gi
import ezhil
import tempfile
import threading
import os
import time
import locale

gi.require_version('Gtk','3.0')

from gi.repository import Gtk, GObject, GLib, Pango

# Class from http://python-gtk-3-tutorial.readthedocs.io/en/latest/textview.html?highlight=textbuffer
class SearchDialog(Gtk.Dialog):
    def __init__(self, parent, text=u""):
        Gtk.Dialog.__init__(self, u"தேடு", parent,
            Gtk.DialogFlags.MODAL, buttons=(
            Gtk.STOCK_FIND, Gtk.ResponseType.OK,
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        
        box = self.get_content_area()
        
        label = Gtk.Label(u"உரையில் தேட வேண்டிய சொல்லை இங்கு இடுக:")
        box.add(label)
        
        self.entry = Gtk.Entry()
        self.entry.set_text(text)
        box.add(self.entry)
        self.show_all()
        
    def get_query(self):
        return self.entry.get_text()

class EditorTags:
    def __init__(self,textbuffer):
        self.keyword  = textbuffer.create_tag("keyword",
            weight=Pango.Weight.BOLD,foreground="red")
        self.literal  = textbuffer.create_tag("literal",
            style=Pango.Style.ITALIC,foreground="green")
        self.operator = textbuffer.create_tag("operator",
            weight=Pango.Weight.SEMIBOLD,foreground="blue")
        self.found = textbuffer.create_tag("xfound",
            background="yellow",underline=Pango.Underline.SINGLE)

class Tokenizer:
    # given a piece of text figure out if it is a number, string-literal or
    # a keyword or just plain old text
    def __init__(self):
        self.lexer = ezhil.EzhilLex()
        
    def get_token(self,chunk):
        self.lexer.reset()
        tok = self.lexer.tokenize(chunk)
        return tok
        
    def is_number(self,tok):
        return ezhil.EzhilToken.is_number(tok)
        

class StopWatch(threading.Thread):
    def __init__(self,limit):
        threading.Thread.__init__(self,name="StopWatchThread")
        self.start = -1
        self.elapsed = -1
        self.limit =  limit
        self.stopped = False        
                
    def run(self):
        self.start = time.time()
        print("Startin ... stop watch")
        while (self.time() < self.limit):
            print("Count Down %d"%self.time())
        raise Exception("Timeout - program taking too long to run")
        return
        
    def time(self):
        self.elapsed = time.time() - self.start
        return self.elapsed
        
class EditorState:
    def __init__(self):
        # Gtk builder objects
        self.builder = Gtk.Builder()

        # editor Gtk widgets
        self.window = None
        self.abt_menu = None
        self.exit_btn = None
        self.MenuBar = None
        self.StatusBar = None
        self.textview = None
        self.textbuffer = None
        self.console_textview = None
        self.console_textbuffer = None
        self.sw = None

        # pure editor state
        self.filename = u'untitled.n'
        self.file_modified = False
        self.count = 0

        # cosmetics
        self.TitlePrefix = u" -சுவடு எழுதி"
    
    # was editor code modified ?
    def is_edited(self):
        return self.textbuffer.get_modified()
    
    # editor code info
    def get_doc_info(self):
        r = {'line_count':0,'char_count':0,'modified':False}
        #print(dir(self.textbuffer))
        #print(self.textbuffer)
        r['line_count'] = self.textbuffer.get_line_count()
        r['char_count'] = self.textbuffer.get_char_count()
        r['modified'] = self.is_edited()
        return r
    
class SentinelRunner(threading.Thread):
    def __init__(self,*args):
        self.args = args
        threading.Thread.__init__(self,name="SentinelRunner")
    
    def run(self):
        #print("Kickstarting ...Sentinel")
        try:
            sw = StopWatch(15)
            #sw.start()
            runner = ThreadedRunner()
            GLib.idle_add( lambda : runner.start() )
            #sw.join(10)
            if runner.isAlive(): 
                runner.join(10)
        except Exception as e:
            print("Stopping thread due to %s"%e)
        return
    
class ThreadedRunner(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self,name="ThreadedEzhilEvaluator")
    
    @staticmethod
    def update_fcn(args):
        res_std_out,is_success=args
        ed = Editor.get_instance()
        ed.console_buffer.set_text( res_std_out )
        ed.StatusBar.push(0,"File %s ran %s"%(ed.filename,["with errors","without errors"][is_success]))
        return
        
    def run(self):
        #print("Kickstarting ... ThreadedRunner")
        
        ezhil.EzhilCustomFunction.set(Editor.dummy_input)
        
        ed = Editor.get_instance()
        if ( ed.is_edited() ):
            #document is edited but not saved;
            msg = u"உங்கள் நிரல் சேமிக்க பட வேண்டும்! அதன் பின்னரே இயக்கலாம்"
            title = u"இயக்குவதில் பிழை"
            dialog = Gtk.MessageDialog(ed.window, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, title) #"Output of Ezhil Code:"
            dialog.format_secondary_text(msg) #res.std_out
            dialog.run()
            dialog.destroy() #OK or Cancel don't matter
            return False
        filename = ed.filename
        
        old_stdin = sys.stdin
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        is_success = False
        tmpfilename = tempfile.mktemp()+".n"
        res_std_out = u""
        old_exit = sys.exit
        sys.exit = Editor.dummy_exit
        try:
            sys.stdout = codecs.open(tmpfilename,"w","utf-8")
            sys.stderr = sys.stdout;
            executer = ezhil.EzhilFileExecuter(filename)
            executer.run()
            is_success = True
        except Exception as e:
            print(u"Failed executing file '{0}':\n{1}'".format(filename, unicode(e)))
        finally:
            sys.exit = old_exit
            sys.stdout.flush()
            sys.stdout.close()
            with codecs.open(tmpfilename,u"r",u"utf-8") as fp:
                res_std_out = fp.read()
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            sys.stdin = old_stdin
            ezhil.EzhilCustomFunction.reset()
        GLib.idle_add( ThreadedRunner.update_fcn, [ res_std_out,is_success ])
        #print("All done")
        return None

class Editor(EditorState):
    _instance = None
    def __init__(self,filename=None):
        EditorState.__init__(self)
        Editor._instance = self
        self.builder.add_from_file("editor.glade")

        
        if filename:
            self.filename = filename
        
        ## construct the GUI from GLADE
        self.window = self.builder.get_object("ezhilEditorWindow")
        self.set_title()
        
        self.console_textview = self.builder.get_object("codeExecutionTextView")
        self.console_textview.set_editable(False)
        self.console_textview.set_cursor_visible(False)
        self.console_buffer = self.console_textview.get_buffer()
        
        self.textview = self.builder.get_object("codeEditorTextView")
        self.StatusBar = self.builder.get_object("editorStatus")
        self.textbuffer = self.textview.get_buffer()
        self.tags = EditorTags(self.textbuffer)
        self.tag_found = self.textbuffer.create_tag("found",
            background="yellow")
        # connect abt menu and toolbar item
        self.abt_menu = self.builder.get_object("aboutMenuItem")
        self.abt_menu.connect("activate",Editor.show_about_status)
        
        self.abt_btn = self.builder.get_object("AboutBtn")
        self.abt_btn.connect("clicked",Editor.show_about_status)
    
        search_menu = self.builder.get_object("search_item")
        search_menu.connect("activate",Editor.on_search_clicked) 
        # open : editor action
        self.open_menu = self.builder.get_object("openMenuItem")
        self.open_menu.connect("activate",Editor.open_file)
        self.open_btn = self.builder.get_object("OpenBtn")
        self.open_btn.connect("clicked",Editor.open_file)

        # new : editor action
        self.new_menu = self.builder.get_object("newMenuItem")
        self.new_menu.connect("activate",Editor.reset_new)
        self.new_btn = self.builder.get_object("NewBtn")
        self.new_btn.connect("clicked",Editor.reset_new)
        
        # run : editor action
        #self.run_menu = self.builder.get_object("runMenuItem")
        #self.run_menu.connect("activate",Editor.run_ezhil_code)
        self.run_btn = self.builder.get_object("RunBtn")
        self.run_btn.connect("clicked",Editor.run_ezhil_code)
        
        # save : editor action save
        self.save_btn = self.builder.get_object("SaveBtn")
        self.save_btn.connect("clicked",Editor.save_file)
        
        # clear buffer : clear run buffer
        self.clear_btn = self.builder.get_object("clearbuffer")
        self.clear_btn.connect("clicked",Editor.clear_buffer)
        
        # hookup the exit
        self.exit_btn = self.builder.get_object("ExitBtn")
        self.exit_btn.connect("clicked",Editor.exit_editor)
        self.exit_menu = self.builder.get_object("quitMenuItem")
        self.exit_menu.connect("activate",Editor.exit_editor)
        # exit by 'x' btn
        self.window.connect("destroy",Editor.exit_editor)
        self.window.show_all()
        
        self.load_file()
        Gtk.main()
    
    # update title
    def set_title(self):
        self.window.set_title(self.filename + self.TitlePrefix)
    
    @staticmethod
    def clear_buffer(menuitem,arg1=None):
        ed = Editor.get_instance()
        ed.console_buffer.set_text(u"")
        ed.StatusBar.push(0,u"Evaluate buffer cleared")
    
    @staticmethod
    def reset_new(menuitem,arg1=None):
        ed = Editor.get_instance()
        ed.count += 1
        ed.filename = u"untitled_%d"%ed.count
        ed.set_title()
        ed.textbuffer = ed.textview.get_buffer()
        ed.textbuffer.set_text("")
        ed.textbuffer.set_modified(False)
        ed.console_buffer = ed.console_textview.get_buffer()
    
    @staticmethod
    def alert_dialog(title,msg,use_ok_cancel=False):
        ed = Editor.get_instance()
        if use_ok_cancel:
            dialog = Gtk.MessageDialog(ed.window, 0, Gtk.MessageType.QUESTION,
                              Gtk.ButtonsType.OK_CANCEL, title)
        else:
            dialog = Gtk.MessageDialog(ed.window, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, title) #"Output of Ezhil Code:"
        dialog.format_secondary_text(msg) #res.std_out
        response = dialog.run()
        dialog.destroy() #OK or Cancel don't matter
        return response
    
    # process based function
    @staticmethod
    def old_run_ezhil_code(menuitem,arg1=None):
        ed = Editor.get_instance()
        filename = ed.filename
        TIMEOUT=45
        #print("Name => ",filename)
        cmd = "ezhili {0}".format(filename.replace("\\","/"))
        
        # blocks upto TIMEOUT seconds
        res = envoy.run(cmd, timeout=TIMEOUT)
        is_success = True if res.status_code == 0 else False
        #print {'result': res.std_out, 'is_success': is_success}
        
        ed.console_buffer.set_text( res.std_out )        
        ed.StatusBar.push(0,"File %s ran %s"%(ed.filename,["with errors","without errors"][is_success]))
        
        return None

    @staticmethod
    def dummy_exit(*args):
        #print(u"Dummy exit function")
        return 0
    
    @staticmethod
    def dummy_input(*args):
        message= not args and "Enter Input" or args[0]
        if not args or len(args) < 2:
            title = "Ezhil language IDE"
        else:
            title = args[1]
        
        ed = Editor.get_instance()
        dialogWindow = Gtk.MessageDialog(ed.window,
                              Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
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
        dialogWindow.destroy()
        if (response == Gtk.ResponseType.OK) and (text != ''):
            return text
        return ""
    
    @staticmethod
    def run_ezhil_code(menuitem,arg1=None):
        runner = ThreadedRunner();
        runner.run()
        GLib.idle_add( lambda :  runner.is_alive() and runner.join() or None )
        while runner.is_alive() and Gtk.events_pending():
            Gtk.main_iteration()
        return
    
    @staticmethod
    def save_file(menuitem,arg1=None):
        ed = Editor.get_instance()
        textbuffer = ed.textview.get_buffer()
        
        if ed.filename.find("untitled") >= 0:        
            dialog = Gtk.FileChooserDialog("நிரலை சேமிக்கவும்:", ed.window,
                Gtk.FileChooserAction.SAVE,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                 Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
            Editor.add_filters(dialog)
            response = dialog.run()
            if response == Gtk.ResponseType.CANCEL:
                dialog.destroy()
                print("Dismiss save dialog - not saved!")
                return
            if dialog.get_filename():
                ed.filename = dialog.get_filename()
            dialog.destroy()
        if ed.filename is not "":
            textbuffer = ed.textview.get_buffer()
        filename = ed.filename
        print("Saved File: " + filename)
        ed.StatusBar.push(0,"Saved File: " + filename)
        index = filename.replace("\\","/").rfind("/") + 1
        text = textbuffer.get_text(textbuffer.get_start_iter() , textbuffer.get_end_iter(),True)
        ed.window.set_title(filename[index:] + ed.TitlePrefix)
        try:
            with codecs.open(filename, "r+","utf-8") as file:
                file.write(text.decode("utf-8"))
                file.close()
        except IOError as ioe:
            # new file:
            with codecs.open(filename, "w","utf-8") as file:
                file.write(text.decode("utf-8"))
                file.close()
        textbuffer.set_modified(False)
        return
    
    ## open handler
    @staticmethod
    def open_file(menuitem, arg1=None):
        textview = Editor.get_instance().textview
        Window = Editor.get_instance().window
        StatusBar = Editor.get_instance().StatusBar

        textbuffer = textview.get_buffer()
        chooser = Gtk.FileChooserDialog("நிரலை திறக்கவும்:", Window,
        Gtk.FileChooserAction.OPEN,(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        Editor.add_filters(chooser)
        textbuffer.set_modified(False)
        response = chooser.run()
        if response == Gtk.ResponseType.OK:
            filename = chooser.get_filename()
            ed = Editor.get_instance()
            ed.filename = filename
            ed.load_file()
            chooser.destroy()
        elif response == Gtk.ResponseType.CANCEL:
            chooser.destroy()
        else:
            chooser.destroy()
        return
    
    def load_file(self):
        ed = Editor.get_instance()
        textview = Editor.get_instance().textview
        Window = Editor.get_instance().window
        StatusBar = Editor.get_instance().StatusBar
        filename = ed.filename
        textbuffer = textview.get_buffer()
        #print("Opened File: " + filename)
        StatusBar.push(0,"Opened File: " + filename)
        #print("file =>",filename)
        Window.set_title(filename + u" - சுவடு எழுதி")
        file = open(filename, "r")
        text = file.read()
        #print("Setting buffer to contents =>",text)
        textbuffer.set_text(text)
        textview.set_buffer(textbuffer)
        textbuffer.set_modified(False)
        file.close()
        return
        
    @staticmethod
    def on_search_clicked(*args_to_ignore):
        ed = Editor.get_instance()
        dialog = SearchDialog(ed.window)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            cursor_mark = ed.textbuffer.get_insert()
            start = ed.textbuffer.get_iter_at_mark(cursor_mark)
            if start.get_offset() == ed.textbuffer.get_char_count():
                start = ed.textbuffer.get_start_iter()

            ed.search_and_mark(dialog.entry.get_text(), start)

        dialog.destroy()

    def search_and_mark(self, text, start):
        end = self.textbuffer.get_end_iter()
        match = start.forward_search(text, 0, end)

        if match != None:
            match_start, match_end = match
            self.textbuffer.apply_tag(self.tag_found, match_start, match_end)
            self.search_and_mark(text, match_end)

    ## miscellaneous signal handlers
    @staticmethod
    def exit_editor(exit_btn):
        ed = Editor.get_instance()
        if ed.is_edited():
            okcancel=True
            respo = Editor.alert_dialog(u"நிரலை சேமிக்கவில்லை",u"உங்கள் நிரல் மாற்றப்பட்டது; இதனை சேமியுங்கள்!",okcancel)
            if respo == Gtk.ResponseType.OK:
                Editor.save_file(None)
        Gtk.main_quit()
    
    @staticmethod
    def abt_dlg_closer(abt_dlg,event):
        abt_dlg.destroy()

    # About status dialog
    @staticmethod
    def show_about_status(*args):
        builder = Gtk.Builder()
        builder.add_from_file("editor.glade")
        abt_menu = args[0]
        abt_dlg = builder.get_object("ezhilAboutDialog")
        #Parent = builder.get_object("ezhilEditorWindow"))
        abt_dlg.show_all()
        ed = Editor.get_instance()
        print(ed.get_doc_info())
        close_btn = builder.get_object("aboutdialog-action_area1")
        abt_dlg.connect("response",Editor.abt_dlg_closer)
        return True

    # filters / utilities
    @staticmethod
    def add_filters(chooser):
        filter = Gtk.FileFilter()
        items = (("Ezhil Files","text/x-ezhil","*.n"),
        ("Text Files","text/data","*.txt"),
        ("All Files","text/data","*.*"))

        for data in items:
            name,mtype,patt = data
            filter = Gtk.FileFilter()
            filter.set_name(name)
            filter.add_mime_type(mtype)
            filter.add_pattern(patt)
            chooser.add_filter(filter)
        return

    # Singleton business
    @staticmethod
    def get_instance():
        return Editor._instance

    @staticmethod
    def set_instance(newinst):
        Editor._instance = newinst
        return Editor._instance

if __name__ == u"__main__":
    os.putenv('LANG','ta_IN.utf8')
    GObject.threads_init()
    Editor(len(sys.argv) > 1 and sys.argv[1] or None)
