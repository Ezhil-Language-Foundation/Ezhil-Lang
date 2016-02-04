#!/usr/bin/env python
##This Python file uses the following encoding: utf-8
##
## (C) 2016 Muthiah Annamalai,
## Licensed under GPL Version 3
##
import codecs
import sys
import envoy
import gi
import ezhil
import tempfile
import threading
import os

gi.require_version('Gtk','3.0')

from gi.repository import Gtk, GObject, GLib

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
        self.TitlePrefix = " - Suvadu/Ezhuthi"

class ThreadedRunner(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    
    @staticmethod
    def update_fcn(args):
        res_std_out,is_success=args
        ed = Editor.get_instance()
        ed.console_buffer.set_text( res_std_out )
        ed.StatusBar.push(0,"File %s ran %s"%(ed.filename,["with errors","without errors"][is_success]))
        return
        
    def run(self,menuitem,arg1=None):
        ezhil.EzhilCustomFunction.set(Editor.dummy_input)
        
        ed = Editor.get_instance()
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
        
        return None

class Editor(EditorState):
    _instance = None
    def __init__(self):
        EditorState.__init__(self)
        Editor._instance = self
        self.builder.add_from_file("editor.glade")

        ## construct the GUI from GLADE
        self.window = self.builder.get_object("ezhilEditorWindow")
        self.set_title()
        
        self.console_textview = self.builder.get_object("codeExecutionTextView")
        self.console_textview.set_editable(False)
        self.console_textview.set_cursor_visible(False)
        self.console_buffer = self.console_textview.get_buffer()
        
        self.textview = self.builder.get_object("codeEditorTextView")
        self.StatusBar = self.builder.get_object("editorStatus")
        
        # connect abt menu and toolbar item
        self.abt_menu = self.builder.get_object("aboutMenuItem")
        self.abt_menu.connect("activate",Editor.show_about_status)
        
        self.abt_btn = self.builder.get_object("AboutBtn")
        self.abt_btn.connect("clicked",Editor.show_about_status)

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
        
        # hookup the exit
        self.exit_btn = self.builder.get_object("ExitBtn")
        self.exit_btn.connect("clicked",Editor.exit_editor)
        self.exit_menu = self.builder.get_object("quitMenuItem")
        self.exit_menu.connect("activate",Editor.exit_editor)
        # exit by 'x' btn
        self.window.connect("destroy",Editor.exit_editor)
        
        self.window.show_all()
        Gtk.main()

    # update title
    def set_title(self):
        self.window.set_title(self.filename + self.TitlePrefix)

    @staticmethod
    def reset_new(menuitem,arg1=None):
        ed = Editor.get_instance()
        ed.count += 1
        ed.filename = u"untitled_%d"%ed.count
        ed.set_title()
        ed.textbuffer = ed.textview.get_buffer()
        ed.textbuffer.set_text("")
        ed.console_buffer = ed.console_textview.get_buffer()
    
    @staticmethod
    def alert_dialog(title,msg):
        ed = Editor.get_instance()
        dialog = Gtk.MessageDialog(ed.window, 0, Gtk.MessageType.INFO,
        Gtk.ButtonsType.OK, title) #"Output of Ezhil Code:"
        dialog.format_secondary_text(msg) #res.std_out
        dialog.run()
        dialog.destroy() #OK or Cancel don't matter
        return None

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
        runner.run(menuitem,arg1)
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
        print "Saved File: " + filename
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

        response = chooser.run()
        if response == Gtk.ResponseType.OK:
            filename = chooser.get_filename()
            Editor.get_instance().filename = filename
            textbuffer = textview.get_buffer()
            #print("Opened File: " + filename)
            StatusBar.push(0,"Opened File: " + filename)
            #print("file =>",filename)
            Window.set_title(filename + " - Suvadu")
            file = open(filename, "r")
            text = file.read()
            #print("Setting buffer to contents =>",text)
            textbuffer.set_text(text)
            textview.set_buffer(textbuffer)
            file.close()
            chooser.destroy()
        elif response == Gtk.ResponseType.CANCEL:
            chooser.destroy()
        else:
            chooser.destroy()
        return
    
    ## miscellaneous signal handlers
    @staticmethod
    def exit_editor(exit_btn):
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
    GObject.threads_init()
    Editor()
