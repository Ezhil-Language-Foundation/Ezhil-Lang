#!/usr/bin/python
# -*- coding: utf-8 -*-
## 
## (C) 2017 Ezhil Language Foundation
## Licensed under GPL Version 3
from __future__ import print_function
import tamil
import gi
import sys
import copy

PYTHON3 = (sys.version[0] == '3')
if PYTHON3:
    unicode = str

gi.require_version('Gtk','3.0')
from gi.repository import Gtk, GObject, GLib, Pango

# row 3 extras: 'shift', 'backspace'
# row 4 extras: 'num keypad','escape to language','space','return'
toList = lambda strval: list(tamil.utf8.get_letters(strval))
class OSKeyboard(object):
    def __init__(self,lang,keys3rows,shift_keys3rows):
        object.__init__(self)
        self.lang = lang
        self.full_space = []
        self.numeric3rows = [ toList(u"1234567890"),toList(u"-/:;()$&@"),toList(u".,?!'") ] 
        self.keys3rows = copy.copy(keys3rows)
        self.shift_keys3rows = copy.copy(shift_keys3rows)
        self.keys3rows_btns = []
        self.spc = u" "*48

    def __str__(self):
        sval = self.lang + u"\n"
        sval += u"\n".join([ u",".join(row) for row in self.keys3rows])
        sval += u"\n---shifted-keys--\n"
        sval += u"\n".join([ u",".join(row) for row in self.shift_keys3rows])
        sval += u"\n---Numeric-keys--\n"
        sval += u"\n".join([ u",".join(row) for row in self.numeric3rows])
        return sval

    def padded(self,key_rows):
        rows2 = key_rows #copy.copy(key_rows)
        if self.lang.find("English") >= 0:
            rows2[-1].insert(0,u"Shift")
            rows2[-1].insert(len(rows2[-1]),u"&lt;- back")
            rows2.append([u"0-9",u"தமிழ்",self.spc+u"Space"+self.spc,u"Enter"])
        else:
            rows2[-1].insert(0,u"பிர")
            rows2[-1].insert(len(rows2[-1]),u"&lt;- அழி")
            rows2.append([u"0-9",u"ஆங்",self.spc+u"வெளி"+self.spc,u"் ",u"இடு"])
        return rows2

    def get_key_modifier(self,key):
        # backspace hook
        if key.find(u"&lt;-") >= 0:
            key = u"\b"
        elif key.find(u"வெளி") >= 0 or key.find(u"Space") >= 0:
            key = u" "
        elif key.find(u"இடு") >= 0 or key.find(u"Enter") >= 0:
            key = u"\n"
        return key

    def build_widget(self,parent_box,edobj):
        rows = list()
        toggle_keys = [u"ஆங்",u"0-9",u"தமிழ்"]
        if ( len(self.keys3rows) < 4 ):
            padded_keys = self.padded(self.keys3rows)
        else:
            padded_keys = self.keys3rows
        del self.keys3rows_btns
        self.keys3rows_btns = list()
        for keys in padded_keys:
            btns = []
            curr_row = Gtk.Box()
            rows.append( curr_row )
            full = False
            for pos,key in enumerate(keys):
                btn = Gtk.Button(label=key)
                btns.append(btn)
                for child in btn.get_children():
                    child.set_label(u"<b>%s</b>"%key)
                    child.set_use_markup(True)
                    break
                key = self.get_key_modifier(key)
                if not key in toggle_keys:
                    btn.connect("clicked",edobj.insert_tamil99_at_cursor,key,self.lang)
                if True: #key in self.full_space:
                    curr_row.pack_start(btn,True,True,2)
                else:
                    curr_row.pack_start(btn,False,False,2)
            curr_row.show_all()
            if True: #full:
                parent_box.pack_start(curr_row,True,True,2)
            else:
                parent_box.pack_start(curr_row,False,False,2)
            self.keys3rows_btns.append(btns)
        return rows

class EnglishKeyboard(OSKeyboard):
    keys3rows = [toList(u"QWERTYUIOP".lower()),toList(u"ASDFGHJKL".lower()),toList(u"ZXCVBNM".lower())]
    shift_keys3rows = [toList(u"QWERTYUIOP"),toList(u"ASDFGHJKL"),toList(u"ZXCVBNM")]
    def __init__(self):
        OSKeyboard.__init__(self,u"English",EnglishKeyboard.keys3rows,EnglishKeyboard.shift_keys3rows)
        self.full_space.append(u"|    Space   |")

class TamilKeyboard(OSKeyboard):
    special = u"புள்ளி"
    space = u"வெளி"
    pulli = u"் "
    keys3rows = [toList(u"ஆஈஊஏளறனடணசஞ"),toList(u"அஇஉஐஎகபமதநய"),[u"ஔ",u"ஓ",u"ஒ",u"வ",u"ங",u"ல",u"ர",u"ழ"]]
    shift_keys3rows = [[u"௧",u"௨",u"௩",u"௪",u"௫",u"௬",u"௭",u"௮",u"௯",u"௦",u"௰"],
                       [u"ஃ",u"ஸ",u"ஷ",u"ஜ",u"ஹ",u"க்ஷ",u"ஶ்ரீ",u"ஶ",u"ௐ",u"௱",u"௲"],
                       [u"௳",u"௴",u"௵",u"௶",u"௷",u"௸",u"௹",u"௺"]]
    def __init__(self):
        OSKeyboard.__init__(self,u"Tamil",TamilKeyboard.keys3rows,TamilKeyboard.shift_keys3rows)
        self.full_space.append(u"    வெளி    ")

class JointKeyboard:
    def __init__(self,parent_box,ed):
        self.parent_box = parent_box
        self.takbd = TamilKeyboard()
        self.enkbd = EnglishKeyboard()
        self.activekbd = self.takbd
        self.ed = ed

    def is_tamil_active(self):
        return self.activekbd == self.takbd

    def is_english_active(self):
        return self.activekbd == self.enkbd

    def build_kbd(self):
        self.clear_parent()
        self.activekbd.build_widget(self.parent_box,self.ed)
        switch_btn = self.activekbd.keys3rows_btns[-1][1]
        switch_btn.connect("clicked", JointKeyboard.callback,self)

    def clear_parent(self):
        kids = self.parent_box.get_children()
        for key_rows in kids[1:]:
            key_rows.destroy()

    def switch_kbd(self):
        if self.is_english_active():
            self.activekbd = self.takbd
        else:
            self.activekbd = self.enkbd

    @staticmethod
    def callback(*args):
        widget = args[0]
        instance = args[1]
        instance.switch_kbd()
        instance.build_kbd()
        return

if __name__ == u"__main__":
    xk = EnglishKeyboard()
    print(str(xk))

    xk = TamilKeyboard()
    print(str(xk))

# Keyboard can manage state 
# It needs Editor obj a actor arg
# Then we have callbacks for keyclks
# These actions update the necessary state of editor
# Editor can bring up the onscreen kbd or not.
