#!/usr/bin/python
##This Python file uses the following encoding: utf-8
##
## (C) 2016 Muthiah Annamalai,
## Licensed under GPL Version 3
##
import sys
import codecs

import gi
import envoy
import tempfile

gi.require_version('Gtk','3.0')
from gi.repository import Gtk

class EditorState:
    def __init__(self):
        self.count = 0;
        self.filename = u'untitled.n'
        self.MenuBar = Gtk.MenuBar()
        self.StatusBar = Gtk.Statusbar()
        self.Window = Gtk.Window()
        self.textview = Gtk.TextView()
        self.textbuffer = None
        self.sw = Gtk.ScrolledWindow()
        self.file_modified = False
            
class Editor(EditorState):
    def __init__(self):
        EditorState.__init__(self)
        Editor.set_instance( self )
        self.construct()
        self.Window.show_all()
        Gtk.main()
        
    def construct(self):
        self.Window.set_title("Ezhil Coding Editor - Suvadu")
        self.Window.set_default_size(800,600)
        self.Window.connect('destroy', Gtk.main_quit)
        
        self.sw.set_hexpand(not True)
        self.sw.set_vexpand(not True)
        vbox = Gtk.VBox(False, 0)
        box0 = Gtk.VBox(False, 0)
        box1 = Gtk.VBox(False, 0)
        box2 = Gtk.VBox(False, 0)
        vbox.pack_start(box0, False, False, 0)
        vbox.pack_start(box1, True, True, 0)
        vbox.pack_start(box2, False, False, 0)
        
        self.textbuffer = self.textview.get_buffer()
        self.textbuffer.set_text("# Enter your code here ... then press run to execute")
        self.sw.add(self.textview)
        box0.pack_start(self.MenuBar, True, False, 0)
        box1.pack_start(self.sw,True,True,0)
        box2.pack_start(self.StatusBar, True, False, 0)
        
        runmenu = Gtk.Menu()
        goitem = Gtk.MenuItem("Go")
        runitem = Gtk.MenuItem("Run")
        runmenu.append(runitem)
        runitem.connect("activate",Editor.run_ezhil_code)
        goitem.set_submenu(runmenu)
        
        filemenu = Gtk.Menu()
        filem,newm,openm,savem,exitm = map( lambda x: Gtk.MenuItem(x), ["File","New","Open","Save","Exit"])
        
        # connect signals
        signal_connector = lambda x: x[0].connect("activate",x[1])
        map( signal_connector, ((openm,Editor.open_file),
        (newm,Editor.reset_new),
        (savem,Editor.save_file),
        (exitm,Gtk.main_quit)))
        
        map( filemenu.append, [newm,openm,savem,exitm])        
        filem.set_submenu(filemenu)
        
        self.MenuBar.append(filem)
        self.MenuBar.append(goitem)
        
        self.Window.add(vbox)
        return

    @staticmethod
    def handle_exit(*args):
        ed = Editor.get_instance()
        if ed.file_modified:
            #say cannot exit and ask user to deal with it
            return
        Gtk.main_quit()
        sys.exit()
        return
    
    @staticmethod
    def open_file(menuitem, arg1=None):
        textview = Editor.get_instance().textview
        Window = Editor.get_instance().Window
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
    
    @staticmethod
    def run_ezhil_code(menuitem,arg1=None):
        ed = Editor.get_instance()
        filename = ed.filename
        TIMEOUT=30
        #print("Name => ",filename)
        cmd = "ezhili {0}".format(filename.replace("\\","/"))
        res = envoy.run(cmd, timeout=TIMEOUT)
        is_success = True if res.status_code == 0 else False
        #print {'result': res.std_out, 'is_success': is_success}
        dialog = Gtk.MessageDialog(ed.Window, 0, Gtk.MessageType.INFO,
        Gtk.ButtonsType.OK, "Output of Ezhil Code:")
        dialog.format_secondary_text(res.std_out)
        dialog.run()
        dialog.destroy() #OK or Cancel don't matter
        #print("INFO dialog closed")
        return None
        
    @staticmethod
    def reset_new(menuitem,arg1=None):
        ed = Editor.get_instance()
        ed.count += 1
        ed.Window.set_title(u"untitled_%d - Suvadu"%ed.count)
        ed.textbuffer = ed.textview.get_buffer()
        ed.textbuffer.set_text("")
        ed.filename = u"untitled_%d"%ed.count
    
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
        ed.Window.set_title(filename[index:] + " - Suvadu")
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

    @staticmethod
    def get_instance( ):
        return Editor._instance
    
    @staticmethod
    def set_instance( obj ):
        Editor._instance = obj
        return obj

if __name__ == u"__main__":
    Editor()
