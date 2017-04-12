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
import time

import gi
import tamil

import OSKeyboardWidget
import ezhil
from DocView import DocBrowserWindow
from ExampleHelper import ExampleBrowserWindow
from SplashActivity import SplashActivity
from syntaxhighlighing import EzhilSyntaxHighlightingEditor
from iyakki import MPRunner

PYTHON3 = (sys.version[0] == '3')
if PYTHON3:
    unicode = str

gi.require_version('Gtk','3.0')

from gi.repository import Gtk, GObject, GLib, Pango
from undobuffer import UndoableBuffer

# This section of code is borrowed from https://github.com/pyinstaller/pyinstaller/wiki/Recipe-Multiprocessing
# override multiprocessing pipe in Windows for packaging purposes.
try:
    # Python 3.4+
    if sys.platform.startswith('win'):
        import multiprocessing.popen_spawn_win32 as forking
    else:
        import multiprocessing.popen_fork as forking
except ImportError:
    import multiprocessing.forking as forking

if sys.platform.startswith('win'):
    # First define a modified version of Popen.
    class _Popen(forking.Popen):
        def __init__(self, *args, **kw):
            if hasattr(sys, 'frozen'):
                # We have to set original _MEIPASS2 value from sys._MEIPASS
                # to get --onefile mode working.
                os.putenv('_MEIPASS2', sys._MEIPASS)
            try:
                super(_Popen, self).__init__(*args, **kw)
            finally:
                if hasattr(sys, 'frozen'):
                    # On some platforms (e.g. AIX) 'os.unsetenv()' is not
                    # available. In those cases we cannot delete the variable
                    # but only set it to the empty string. The bootloader
                    # can handle this case.
                    if hasattr(os, 'unsetenv'):
                        os.unsetenv('_MEIPASS2')
                    else:
                        os.putenv('_MEIPASS2', '')

    # Second override 'Popen' class with our modified version.
    forking.Popen = _Popen

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

class EditorState:
    def __init__(self):
        # Gtk builder objects
        self.builder = Gtk.Builder()
        
        # timing logger
        self.tstart = 0.0
        self.tend = 0.0

        # font settings
        self.default_timeout = 60
        self.default_font = u"Sans Italic 16"
        self.fontsel = None

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
        self.autorun = False
        # pure editor state
        self.filename = os.path.join(u'examples',u'untitled.n')
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

class Editor(EditorState, EzhilSyntaxHighlightingEditor):
    _instance = None
    def __init__(self,filename=None,autorun=False):
        EditorState.__init__(self)
        EzhilSyntaxHighlightingEditor.__init__(self)
        Editor._instance = self
        self.autorun = autorun
        self.builder.add_from_file("res/editor.glade")
        if filename:
            self.filename = filename
        ## construct the GUI from GLADE
        self.window = self.builder.get_object("ezhilEditorWindow")
        try:
            self.window.set_icon_from_file("res/img/ezhil_square_2015_128px.png")
        except Exception as ie:
            pass
        self.window.set_resizable(True)
        self.window.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.console_textview = self.builder.get_object("codeExecutionTextView")

        self.help_browser = None
        self.example_browser = None
        self.menuKbd = self.builder.get_object("toggleKeyboard")
        self.menuKbd.connect("activate", lambda wid: self.toggleKeyboard(wid))
        self.toolitemKbd = self.builder.get_object("KbdBtn")
        self.toolitemKbd.connect("clicked",lambda wid: self.toggleKeyboardAndKeyword(wid))
        
        self.exampleMenu = self.builder.get_object("exampleBrowserItem")
        self.exampleMenu.connect("activate",lambda wid: self.exampleBrowser(wid))

        self.helpItem = self.builder.get_object("HelpBtn")
        self.helpItem.connect("clicked",lambda wid: self.helpBrowser(wid))
        self.helpMenuItem = self.builder.get_object("helpMenuItem")
        self.helpMenuItem.connect("activate",lambda wid: self.helpBrowser(wid))

        self.toolitemFont = self.builder.get_object("FontBtn")
        self.toolitemFont.connect("clicked", lambda wid: self.chooseFont(wid))

        self.menuKeyword = self.builder.get_object("toggleKeyword")
        self.menuKeyword.connect("activate",lambda wid: self.toggleKeyword(wid))

        ## self.console_textview.set_editable(False)
        self.console_textview.set_cursor_visible(False)
        self.console_textview.set_buffer(UndoableBuffer())
        self.console_buffer = self.console_textview.get_buffer()
        self.scrolled_codeview = self.builder.get_object("scrolledwindow1")
        self.textview = self.builder.get_object("codeEditorTextView")
        self.StatusBar = self.builder.get_object("editorStatus")
        self.textview.set_buffer(UndoableBuffer())
        self.textbuffer = self.textview.get_buffer()
        self.scrolled_codeview.set_policy(Gtk.PolicyType.AUTOMATIC,Gtk.PolicyType.AUTOMATIC)
        self.tag_text = None
        self.tag_literal = None
        self.tag_comment = None
        self.tag_fail = None
        self.tag_found = None
        self.tag_operator = None
        self.tag_pass = None
        self.refresh_tags()
        # add keywords bar
        self.keywords8 = [u"பதிப்பி",u"முடி",u"நிரல்பாகம்",u"தொடர்",u"நிறுத்து",u"ஒவ்வொன்றாக",u"இல்",u"ஆனால்",u"இல்லைஆனால்",u"இல்லை", u"ஆக",u"வரை",u"பின்கொடு",]
        self.operators16 = [u"@",u"+",u"-",u"*",u"/",u"%",u"^",u"==",u">",u"<",u">=",u"<=",u"!=",u"!=",u"!",u",",u"(",u")",u"{",u"}",u"()",u"[]"]
        self.forms = [u"@(  )\t ஆனால் \n இல்லை  \n முடி",u" @(  )\t வரை \n முடி",u"நிரல்பாகம்\t உதாரணம் () \n முடி"]

        self.widget_keywords = self.builder.get_object("hbox_keywords8")
        self.widget_operators = self.builder.get_object("hbox_operators16")
        self.widget_forms = self.builder.get_object("hbox_forms")
        self.build_keyword_btns()

        # on screen keyboard
        self.editorBox = self.builder.get_object("editorBox")
        self.oskeyboard = None
        self.toggleKeyboard()

        # connect abt menu and toolbar item
        self.abt_menu = self.builder.get_object("aboutMenuItem")
        self.abt_menu.connect("activate",Editor.show_about_status)
        
        self.abt_btn = self.builder.get_object("AboutBtn")
        self.abt_btn.connect("clicked",Editor.show_about_status)

        self.cut_menu = self.builder.get_object("cut_item")
        self.cut_menu.connect("activate",Editor.cut_action)

        self.paste_menu = self.builder.get_object("paste_item")
        self.paste_menu.connect("activate",Editor.paste_action)

        self.cp_menu = self.builder.get_object("copy_item")
        self.cp_menu.connect("activate",Editor.copy_action)

        # for undo-redo buttons
        self.undo_btn = self.builder.get_object("UndoBtn")
        self.redo_btn = self.builder.get_object("RedoBtn")
        self.undo_btn.connect("clicked",Editor.undo_action)
        self.redo_btn.connect("clicked",Editor.redo_action)

        # for code textview
        #self.textview.connect("backspace",Editor.on_codebuffer_edited)
        #self.textview.connect("delete-from-cursor",Editor.on_codebuffer_edited)
        #self.textview.connect("insert-at-cursor",Editor.on_codebuffer_edited)
        
        # search action in text buffer
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
        self.run_menu = self.builder.get_object("runMenuItem")
        self.run_menu.connect("activate",Editor.run_ezhil_code)
        self.run_btn = self.builder.get_object("RunBtn")
        run_signal = self.run_btn.connect("clicked",Editor.run_ezhil_code)
        
        # save : editor action save
        self.save_btn = self.builder.get_object("SaveBtn")
        self.save_btn.connect("clicked",Editor.save_file)
        self.save_menu = self.builder.get_object("menuItemSave")
        self.save_menu.connect("activate",Editor.save_file)
        self.saveas_menu = self.builder.get_object("menuItemSaveAs")
        self.saveas_menu.connect("activate",Editor.saveas_file)

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
        if autorun:
            self.do_autorun()
        #self.textbuffer.connect_after('insert-text', Editor.keep_syntax_highlighting_on)
        #self.textbuffer.connect_after('delete-range', Editor.keep_syntax_highlighting_on)
        #GLib.timeout_add(5000, Editor.keep_syntax_highlighting_on )
        #Gtk.main()

    def do_autorun(self):
        GLib.timeout_add(1000,lambda : self.run_btn.emit("clicked") )
        return

    def refresh_tags(self):
        if not self.tag_text:
            # for console buffer
            self.tag_fail  = self.console_buffer.create_tag("fail",
                weight=Pango.Weight.SEMIBOLD,font=self.default_font,foreground="red")
            self.tag_pass  = self.console_buffer.create_tag("pass",
                weight=Pango.Weight.SEMIBOLD,font=self.default_font,foreground="green")

        EzhilSyntaxHighlightingEditor.refresh_tags(self)


    def update_font(self):
        if not self.fontsel:
            return
        self.default_font = self.fontsel.get_font_name()
        self.refresh_tags()


    # update title
    def set_title(self):
        self.window.set_title(self.filename + self.TitlePrefix)

    # callback for font button:
    def chooseFont(self,widget):
        fontDlg = Gtk.FontSelectionDialog(parent=self.window,title="choose a font please")
        fontDlg.set_size_request(550,400)
        fontDlg.set_font_name(self.default_font)
        fontDlg.set_preview_text(u"The quick brown fox jumped over the lazy dog. தமிழில் நிரல் எழுது – Write code in தமிழ் எழில் : தமிழ் நிரலாக்க மொழி")
        res = fontDlg.run()
        if res == Gtk.ResponseType.OK:
            self.fontsel = fontDlg.get_font_selection()
            #print(self.fontsel.get_font_name())
            self.update_font()
        
        fontDlg.destroy()
        return True

    def drop_ref_to_exampleBrowser(self,*args):
        self.example_browser.destroy()
        self.example_browser = None
        return True
    
    def exampleBrowser(self,*arg):
        if not self.example_browser:
            self.example_browser = ExampleBrowserWindow(self)
            self.example_browser.connect("delete_event",lambda *wid: self.drop_ref_to_exampleBrowser(*wid))
        self.example_browser.present()

    def drop_ref_to_helpBrowser(self,*args):
        self.help_browser.window.destroy()
        self.help_browser = None
        return True

    def helpBrowser(self,*arg):
        if not self.help_browser:
            self.help_browser = DocBrowserWindow(self,self.default_font)
            self.help_browser.window.connect("delete_event",lambda *wid: self.drop_ref_to_helpBrowser(*wid))
        self.help_browser.window.present()

    def toggleKeyboardAndKeyword(self,*arg):
        try:
            self.toggleKeyboard(*arg)
        except Exception as ie:
            pass
        try:
            self.toggleKeyword(*arg)
        except Exception as ie:
            pass
        return True

    # callback for toggle keyboard
    def toggleKeyboard(self,*args):
        if self.oskeyboard != None:
            self.oskeyboard.clear_parent()
            del self.oskeyboard
            self.oskeyboard = None
            self.editorBox.set_child_packing(self.scrolled_codeview,True,True,0,0)
        else:
            self.oskeyboard = OSKeyboardWidget.JointKeyboard(self.editorBox,self)
            self.oskeyboard.build_kbd()
        return True

    # callback for toggle keyboard
    def toggleKeyword(self,*args):
        if self.widget_keywords.get_visible():
            self.widget_keywords.hide()
            self.widget_forms.hide()
            self.widget_operators.hide()
        else:
            self.widget_keywords.show()
            self.widget_forms.show()
            self.widget_operators.show()
        return True

    def build_keyword_btns(self):
        for kw in self.keywords8:
            btn = Gtk.Button(kw)
            self.widget_keywords.pack_start( btn,True, True, 0)
            btn.connect("clicked",Editor.insert_at_cursor,kw)
            btn.show()

        for kw in self.operators16:
            btn = Gtk.Button(kw)
            self.widget_operators.pack_start( btn,True, True, 0)
            btn.connect("clicked",Editor.insert_at_cursor,kw)
            btn.show()

        for kw in self.forms:
            btn = Gtk.Button(u" ".join(re.split("\s+",kw)))
            self.widget_forms.pack_start( btn, True, True, 0)
            btn.connect("clicked",Editor.insert_at_cursor,kw)
            btn.show()
            
    @staticmethod
    def update_fcn(args):
        res_std_out,is_success=args
        ed = Editor.get_instance()
        ed.tend = time.time()
        time_desc = u" %0.3g வினாடி"%(ed.tend - ed.tstart)
        ed.console_buffer.set_text( res_std_out )
        tag = is_success and ed.tag_pass or ed.tag_fail
        start = ed.console_buffer.get_start_iter()
        end = ed.console_buffer.get_end_iter()
        ed.console_buffer.apply_tag(tag,start,end)
        ed.StatusBar.push(0,u"உங்கள் நிரல் '%s' %s %s நேரத்தில் இயங்கி முடிந்தது"%(ed.filename,[u"பிழை உடன்",u"பிழையில்லாமல்"][is_success],time_desc))
        if ed.autorun:
            for i in range(1):
                time.sleep(1)
                Gtk.main_iteration()
            sys.exit(not is_success)
        return

    @staticmethod
    def insert_at_cursor(widget,value):
        ed = Editor.get_instance()
        ed.textbuffer.insert_at_cursor(value)
        return True

    # Implements Tamil-99 keyboard
    @staticmethod
    def insert_tamil99_at_cursor(widget,value,lang=u"Tamil"):
        ed = Editor.get_instance()
        m_start = ed.textbuffer.get_iter_at_mark(ed.textbuffer.get_insert())

        # handle special characters
        if value == u"\b":
            ed.textbuffer.backspace(m_start,False,True)
            ed.textview.place_cursor_onscreen()
            return
        elif value == u"் ":
            ed.textbuffer.insert_at_cursor(value)
            ed.textview.place_cursor_onscreen()
            return

        # dispose of English language stuff
        if lang.lower().find("eng") >= 0:
            Editor.insert_at_cursor(widget,value)
            return

        if not m_start.starts_line():
            offset = m_start.get_offset()
            m_prev = ed.textbuffer.get_iter_at_offset(offset-1)
            old_value = ed.textbuffer.get_text(m_prev,m_start,True)
            # encoding conversion
            if not PYTHON3:
                try:
                    old_value = old_value.decode("UTF-8")
                except Exception as e:
                    pass

            if old_value.find(u"் ") >= 0:
                ed.textbuffer.insert_at_cursor(value)
                return

            # Odd GTK bug - where pulli as previous char before cursor
            # will not be retrieved in the offset-1 position so we need to do some
            # sleuthing.
            if old_value == " " and tamil.utf8.is_tamil_unicode(value):
                try:
                    m_prev = ed.textbuffer.get_iter_at_offset(offset-2)
                    old_value = ed.textbuffer.get_text(m_prev,m_start,True)
                    if not PYTHON3:
                        try:
                            old_value = old_value.decode("UTF-8")
                        except Exception as decodeerror:
                            pass

                    if old_value.find(u"் ") >= 0:
                        ed.textbuffer.backspace(m_start,False,True)
                        ed.textbuffer.insert_at_cursor(value)
                        return

                except Exception as decodeerror:
                    pass


            #print(u"%s"%old_value)
            #print(u"%s"%value)
            try:
                uyir_idx = tamil.utf8.uyir_letters.index(value)
                mei_idx = tamil.utf8.agaram_letters.index(old_value)
                value = tamil.utf8.uyirmei_constructed(mei_idx, uyir_idx)
                ed.textbuffer.backspace(m_start,False,True)
            except Exception as e:
                pass
                #print(PYTHON3 and str(e) or str(e).decode("UTF-8")

        ed.textbuffer.insert_at_cursor(value)
        ed.textview.place_cursor_onscreen()
        return True

    @staticmethod
    def get_license_text():
        txt = u"GPL v-3"
        try:
            with codecs.open(u"res/LICENSE_notes.txt","r","UTF-8") as fp:
                txt = fp.read()
        except IOError as ioe:
            pass
        return txt

    @staticmethod
    def redo_action(*args):
        ed = Editor.get_instance()
        if not ed.textbuffer.can_redo:
            ed.StatusBar.push(0,u"திருத்தியில் மீட்க்க எதுவும் இல்லை")
            return
        ed.textbuffer.redo()
    
    @staticmethod
    def undo_action(*args):
        ed = Editor.get_instance()
        if not ed.textbuffer.can_undo:
            ed.StatusBar.push(0,u"திருத்தியில் மாற்ற எதுவும் இல்லை")
            return
        ed.textbuffer.undo()
    
    # todo - at every keystroke we need to run the syntax highlighting
    @staticmethod
    def on_codebuffer_edited(*args):
        ed = Editor.get_instance()
        mrk_start = ed.textbuffer.get_insert()
        m_start = ed.textbuffer.get_iter_at_mark(mrk_start)
        mrk_end = ed.textbuffer.get_insert()
        m_end = ed.textbuffer.get_iter_at_mark(mrk_end)
        m_end.forward_line()
        while not m_start.starts_line():
            m_start.backward_char()
        text = ed.textbuffer.get_text(m_start,m_end,True)
        try:
            ed.run_syntax_highlighting(text,[m_start,m_end])
        except Exception as e:
            ed.textbuffer.set_text(m_start,m_end,text)
            print(u"skip exception %s"%e)
        return False #callback was not handled AFAIK
    
    @staticmethod
    def keep_syntax_highlighting_on(*args):
        ed = Editor.get_instance()
        if not ed.is_edited():
            return

        start,end = ed.textbuffer.get_bounds()
        text = ed.textbuffer.get_text(start,end,True)
        ed.run_syntax_highlighting(text,[start,end])

        return

    @staticmethod
    def clear_buffer(menuitem,arg1=None):
        ed = Editor.get_instance()
        ed.console_buffer.set_text(u"")
        ed.StatusBar.push(0,u"நிரல் வெளிப்பாடு அழிக்கப்பட்டது")
    
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

    @staticmethod
    def cut_action(*args_ign):
        ed = Editor.get_instance()
        bounds = ed.textbuffer.get_selection_bounds()
        clipboard = Gtk.Clipboard.get_default( ed.window.get_display() )
        ed.textbuffer.cut_clipboard(clipboard,ed.textview.get_editable())

    @staticmethod
    def copy_action(*args_ign):
        ed = Editor.get_instance()
        bounds = ed.textbuffer.get_selection_bounds()
        clipboard = Gtk.Clipboard.get_default( ed.window.get_display() )
        text = ed.textbuffer.get_text(bounds[0],bounds[1],True)
        clipboard.set_text(text,len(text))
        
    @staticmethod
    def paste_action(*args_ign):
        ed = Editor.get_instance()
        clipboard = Gtk.Clipboard.get_default( ed.window.get_display() )
        clipboard.request_text(ed.readclipboard, user_data=None)
		
    #callback for clipboard paste
    def readclipboard(self, clipboard, text, data):
        self.textbuffer.insert_at_cursor(text,len(text))
    
    @staticmethod
    def dummy_exit(*args):
        #(u"Dummy exit function")
        return 0
        
    @staticmethod
    def run_ezhil_code(menuitem,arg1=None):
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
        runner = MPRunner()
        GLib.idle_add( lambda : Gtk.events_pending() and Gtk.main_iteration() )
        ed.tstart = time.time()
        runner.run(ed.filename)
        Editor.update_fcn([runner.res_std_out,runner.is_success])
        return
    
    @staticmethod
    def saveas_file(args):
        try:
            ed = Editor.get_instance()
            old_fn = ed.filename
            ed.filename = u"untitled"
            Editor.save_file(*args)
        except Exception as e:
            ed.filename = old_fn
        finally:
            pass
        
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
                #print("Dismiss save dialog - not saved!")
                return
            if dialog.get_filename():
                ed.filename = dialog.get_filename()
            dialog.destroy()
        if ed.filename is not "":
            textbuffer = ed.textview.get_buffer()
        filename = ed.filename
        #print("Saved File: " + filename)
        ed.StatusBar.push(0,u"உங்களது நிரல் சேமிக்க பட்டது: " + filename)
        index = filename.replace("\\","/").rfind("/") + 1
        text = textbuffer.get_text(textbuffer.get_start_iter() , textbuffer.get_end_iter(),True)
        ed.window.set_title(filename[index:] + ed.TitlePrefix)
        try:
            with codecs.open(filename, "w","utf-8") as file:
                file.write(PYTHON3 and text or text.decode("utf-8"))
                file.close()
        except IOError as ioe:
            # new file:
            with codecs.open(filename, "w","utf-8") as file:
                file.write(PYTHON3 and text or text.decode("utf-8"))
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
    
    def load_file(self,specific_file=None):
        # at this routine all the pre-validations are completed
        ed = Editor.get_instance()
        textview = Editor.get_instance().textview
        Window = Editor.get_instance().window
        StatusBar = Editor.get_instance().StatusBar
        if specific_file:
            ed.filename = specific_file
        filename = ed.filename
        textbuffer = textview.get_buffer()
        #print("Opened File: " + filename)
        StatusBar.push(0, filename+u" - நிரல் திறந்தாச்சு")
        #print("file =>",filename)
        Window.set_title(filename + u" - சுவடு எழுதி")
        try:
            text = u""
            with codecs.open(filename, "r","utf-8") as file:
                text = file.read()
        except IOError as ioe:
            Window.set_title(u"untitled.n - சுவடு எழுதி")
        #("Setting buffer to contents =>",text)
        textview.set_buffer(textbuffer)
        try:
            ed.run_syntax_highlighting(text)
        except Exception as slxe:
            StatusBar.push(0,u"இந்த நிரலை '%s', Syntax Highlighting செய்ய முடியவில்லை"%filename)
            textbuffer.set_text(text)
        textview.scroll_to_iter(textbuffer.get_start_iter(),0.0,not True,0.0,0.0)
        textview.grab_focus()
        textbuffer.set_modified(False)
        return
        
    @staticmethod
    def on_search_clicked(*args_to_ignore):
        ed = Editor.get_instance()
        # clear any previous tags in the space
        ed.textbuffer.remove_tag(ed.tag_found, \
                    ed.textbuffer.get_start_iter(), \
                    ed.textbuffer.get_end_iter())
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

    def show_example(self,filename):
        if self.is_edited():
            respo = Editor.alert_dialog(u"நிரலை சேமிக்கவில்லை",u"உங்கள் நிரல் மாற்றப்பட்டது; இதனை சேமியுங்கள்! அதன் பின்னரே உதாரணங்களை காமிக்க முடியும்",okcancel)
            if respo == Gtk.ResponseType.OK:
                self.load_file(filename)
        else:
            self.load_file(filename)
        return True
    
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
        builder.add_from_file("res/editor.glade")
        abt_menu = args[0]
        abt_dlg = builder.get_object("ezhilAboutDialog")
        #Parent = builder.get_object("ezhilEditorWindow"))
        ed = Editor.get_instance()
        abt_dlg.set_property("license",Editor.get_license_text())
        abt_dlg.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        abt_dlg.show_all()
        #print(ed.get_doc_info())
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

def mainfn(arg_autorun):
        Editor(len(sys.argv) > 1 and sys.argv[1] or None,autorun=arg_autorun)
        Gtk.main()

# TODO - options for 'debug', 'LANG', 'encoding' etc..
if __name__ == u"__main__":
    # show preference for user locale.
    if ( os.getenv('LANG','en_US.utf8').lower().find("ta") == -1 ):
        os.putenv('LANG','ta_IN.utf8')
    multiprocessing.freeze_support()
    GObject.threads_init()
    #debug mode: autorun and quit on the file
    if len(sys.argv) > 2:
        arg_autorun = (sys.argv[2].lower() in [u"-autorun",u"--autorun"])
    else:
        arg_autorun = False

    if os.getenv("TEST_EZHIL_DEVELOPMENT",None):
        mainfn(arg_autorun)
    elif not arg_autorun:
        SplashActivity(lambda : mainfn(arg_autorun))
    else:
        mainfn(arg_autorun)
