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
gi.require_version('Gtk','3.0')

from gi.repository import Gtk

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
    
    @staticmethod
    def run_ezhil_code(menuitem,arg1=None):
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
    def save_file(menuitem,arg1=None):
        ed = Editor.get_instance()
        textbuffer = ed.textview.get_buffer()
        if ed.filename is not "":
            textbuffer = ed.textview.get_buffer()
        filename = ed.filename
        #print "Saved File: " + filename
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
        chooser = Gtk.FileChooserDialog("Please choose a file", Window,
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
        elif response == Gtk.RESPONSE_CANCEL:
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
    Editor()
