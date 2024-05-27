#!/usr/bin/env python
##This Python file uses the following encoding: utf-8
##
## This file is part of the Ezhil Language project.
## 
## (C) 2017 Muthiah Annamalai
## Licensed under GPL Version 3
## Ezhil Language Foundation

import os
import codecs

import gi
gi.require_version('Gtk','3.0')
from gi.repository import Gtk, GLib

from .iyakki import MPRunner
from random import randint
_DEBUG = False

# This class will show a success/failure error message:
class PopupWindow:
    @staticmethod
    def display_message(window,success_flag,text_msg):
        passfail = ["பிழையுடன்","சரியாக"]
        dialog = Gtk.MessageDialog(window, 0, Gtk.MessageType.INFO,
        Gtk.ButtonsType.OK_CANCEL,"எழில் கீற்று இயக்கியதில் %s இயக்கி முடிந்தது."%passfail[int(success_flag)])
        dialog.format_secondary_text(text_msg)
        dialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        response = dialog.run()
        dialog.destroy() #OK or Cancel don't matter
        #if response == Gtk.ResponseType.CANCEL:
        #pass
        #elif response == Gtk.ResponseType.OK:
        #self.settings.set_license_accepted()
        return False

# This class adds two items to popup menuitem
# 
class PopupForTextView(object):
    MODES = frozenset(['EXECUTE_SELECTION','SHOW_HELP'])
    def __init__(self,text_view,mode,ref=None):
        object.__init__(self)
        self.text_view = text_view
        assert( mode in PopupForTextView.MODES)
        self.mode = mode
        self.text_view.connect("populate-popup",PopupForTextView.populateContextMenu,self)
        self.curr_row = ref and ref.curr_row+2 or 100
        self.sepitem = None
        
    def get_selected_text(self):
        tb = self.text_view.get_buffer()
        try:
            (start,end) = tb.get_selection_bounds()
            return tb.get_text(start,end,True)
        except Exception as ex:
            return None
        
    def add_separator(self,popup):
        self.sepitem = Gtk.SeparatorMenuItem.new()
        popup.attach(self.sepitem,0,1,self.curr_row,self.curr_row+1)
        self.sepitem.show()
        self.curr_row += 1
        
    def get_mode_callback_label(self):
        if self.mode == 'EXECUTE_SELECTION':
            return ("இயக்கு",PopupForTextView.executeCallback)
        else:
            return ("உதவி குறிப்பு",PopupForTextView.searchCallback)
        
    @staticmethod
    def searchCallback(menu_item,user_data):
        assert( isinstance(user_data,PopupForTextView) )
        selection = user_data.get_selected_text()
        if not selection:
            return
        #print(u"search/help callback [%s]"%selection)
        
    @staticmethod
    def executeCallback(menu_item,user_data):
        assert( isinstance(user_data,PopupForTextView) )
        selection = user_data.get_selected_text()
        if not selection:
            return
        #print(u"execute callback on [%s]"%selection)
        
        filename = "tmp_%d.ezhil"%randint(0,10000)
        if _DEBUG: print("dummy file => %s"%filename)
        with codecs.open(filename,"wb") as fp:
            fp.write("# Ezhil code snippet\n")
            fp.write(selection)
        window = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)
        try:
            runner = MPRunner(timeout=10)
            GLib.idle_add( lambda : Gtk.events_pending() and Gtk.main_iteration() )
            runner.run(filename)
            if _DEBUG: print(runner.res_std_out)
            PopupWindow.display_message(window,runner.is_success,runner.res_std_out)
        except Exception as ioe:
            if _DEBUG: print("Exception: ",str(ioe))
            PopupWindow.display_message(window=window,success_flag=False,text_msg=str(ioe))
        window.destroy()
        os.unlink(filename)
        
    @staticmethod
    def populateContextMenu(text_view,popup,user_data):
        assert( isinstance(user_data,PopupForTextView) )
        label,cb = user_data.get_mode_callback_label()
        exmnuitem = Gtk.MenuItem.new_with_label(label)
        user_data.add_separator(popup)
        top,bot = user_data.curr_row,user_data.curr_row+1
        user_data.curr_row += 1
        popup.attach(exmnuitem,0,1,top,bot)
        exmnuitem.show()
        exmnuitem.connect("activate",cb,user_data)
