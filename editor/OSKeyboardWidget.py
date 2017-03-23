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
        self.keys3rows = keys3rows
        self.shift_keys3rows = shift_keys3rows
    
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
            rows2[-1].insert(len(rows2[-1]),u"<-")
            rows2.append([u"0-9",u"தமிழ்",u"    Space    ",u"Enter"])
        else:
            rows2[-1].insert(0,u"பிர")
            rows2[-1].insert(len(rows2[-1]),u"&lt;- அழி")
            rows2.append([u"0-9",u"ஆங்கிலம்",u"    வெளி     ",u"் ",u"இடு"])
        return rows2

    def build_widget(self,parent_box,edobj):
        rows = list()
        padded_keys = self.padded(self.keys3rows)
        for keys in padded_keys:
            curr_row = Gtk.Box()
            rows.append( curr_row )
            full = False
            for key in keys:
                btn = Gtk.Button(label=key)
                for child in btn.get_children():
                    child.set_label(u"<b>%s</b>"%key)
                    child.set_use_markup(True)
                    break
                if self.lang.find("English") >= 0:
                    btn.connect("clicked",edobj.insert_at_cursor,key)
                else:
                    btn.connect("clicked",edobj.insert_tamil99_at_cursor,key)
                if True: #key in self.full_space:
                    curr_row.pack_start(btn,True,True,2)
                else:
                    curr_row.pack_start(btn,False,False,2)
            curr_row.show_all()
            if True: #full:
                parent_box.pack_start(curr_row,True,True,2)
            else:
                parent_box.pack_start(curr_row,False,False,2)
        return rows

class EnglishKeyboard(OSKeyboard):
    keys3rows = [toList(u"QWERTYUIOP".lower()),toList(u"ASDFGHJKL".lower()),toList(u"ZXCVBNM".lower())]
    shift_keys3rows = [toList(u"QWERTYUIOP"),toList(u"ASDFGHJKL"),toList(u"ZXCVBNM")]
    def __init__(self):
        OSKeyboard.__init__(self,u"English",EnglishKeyboard.keys3rows,EnglishKeyboard.shift_keys3rows)
        self.full_space.append(u"    Space   ")

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
