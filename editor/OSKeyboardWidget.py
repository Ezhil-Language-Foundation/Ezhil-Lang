#!/usr/bin/python
# -*- coding: utf-8 -*-
## 
## (C) 2017 Ezhil Language Foundation
## Licensed under GPL Version 3

import tamil
import gi
import sys
import copy

PYTHON3 = (sys.version[0] == '3')
if PYTHON3:
    str = str

gi.require_version('Gtk','3.0')
from gi.repository import Gtk

# row 3 extras: 'shift', 'backspace'
# row 4 extras: 'num keypad','escape to language','space','return'
toList = lambda strval: list(tamil.utf8.get_letters(strval))
class OSKeyboard(object):
    def __init__(self,lang,keys3rows,shift_keys3rows):
        object.__init__(self)
        self.lang = lang
        rowlast = toList("=.,?!'")
        rowlast.extend(['&lt;','&gt;','{','}','[',']']) #add <, >, {,}, [,] keys to virtual kbd
        self.numeric3rows = [ toList("1234567890"),toList("-/:;()$&@"),rowlast ]
        self.keys3rows = copy.copy(keys3rows)
        self.shift_keys3rows = copy.copy(shift_keys3rows)
        self.keys3rows_btns = []
        self.mode = "non-numeric"
        self.spc = " "*16
        self.shift_words = ["பிற", "Shift"]
        self.shiftmode = False

    def __str__(self):
        sval = self.lang + "\n"
        sval += "\n".join([ ",".join(row) for row in self.keys3rows])
        sval += "\n---shifted-keys--\n"
        sval += "\n".join([ ",".join(row) for row in self.shift_keys3rows])
        sval += "\n---Numeric-keys--\n"
        sval += "\n".join([ ",".join(row) for row in self.numeric3rows])
        return sval

    def toggle_shift_mode(self):
        self.shiftmode = not self.shiftmode
        return self.shiftmode

    def numericmode(self):
        return self.mode.find("non-numeric") == -1

    def padded(self,key_rows,numerickdb=False):
        rows2 = key_rows #copy.copy(key_rows)
        if self.lang.find("English") >= 0:
            if rows2[-1][0].find("Shift") == -1:
                rows2[-1].insert(0,"Shift")
                rows2[-1].insert(len(rows2[-1]),"&lt;- back")
            rows2.append(["0-9","தமிழ்",self.spc+"Space"+self.spc,"Enter"])
            if numerickdb:
                rows2[-1][1] = "ஆங்"
        else:
            if rows2[-1][0].find("பிற") == -1:
                rows2[-1].insert(0,"பிற")
                rows2[-1].insert(len(rows2[-1]),"&lt;- அழி")
            rows2.append(["0-9","ஆங்",self.spc+"வெளி"+self.spc,"் ","இடு"])
            if numerickdb:
                rows2[-1][1] = "தமிழ்"
        return rows2

    def get_key_modifier(self,key):
        # backspace hook
        if key.find("&lt;-") >= 0:
            key = "\b"
        elif key.find("வெளி") >= 0 or key.find("Space") >= 0:
            key = " "
        elif key.find("இடு") >= 0 or key.find("Enter") >= 0:
            key = "\n"
        elif key == "&amp;":
            key = "&"
        elif key == "&lt;":
            key = "<"
        elif key == "&gt;":
            key = ">"
        return key
    
    def build_widget(self,parent_box,edobj,numerickbd=False):
        if numerickbd:
            self.mode = "numeric"
        else:
            self.mode = "non-numeric"

        rows = list()
        toggle_keys = ["ஆங்","0-9","தமிழ்"]

        #numeric mode cannot have any shift modes

        if numerickbd:
            ref_keys3rows = self.numeric3rows
            ref_keys3rows[1][7] = "&amp;"
        else:
            if self.shiftmode:
                ref_keys3rows = self.shift_keys3rows
            else:
                ref_keys3rows = self.keys3rows

        if ( len(ref_keys3rows) < 4 ):
            padded_keys = self.padded(ref_keys3rows,numerickbd)
        else:
            padded_keys = ref_keys3rows

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
                    if self.lang.find("English") >= 0:
                        child.set_label("<span weight=\"heavy\" size=\"large\" fallback=\"true\">%s</span>"%key)
                    else:
                        child.set_label("<span weight=\"heavy\" size=\"large\" fallback=\"true\">%s</span>"%key)
                    child.set_use_markup(True)
                    break
                key = self.get_key_modifier(key)
                if not any([key in toggle_keys, key in self.shift_words]):
                    btn.connect("clicked",edobj.insert_tamil99_at_cursor,key,self.lang)
                curr_row.pack_start(btn,True,True,2)
            curr_row.show_all()
            parent_box.pack_start(curr_row,False,not True,2)
            self.keys3rows_btns.append(btns)
        return rows

class EnglishKeyboard(OSKeyboard):
    keys3rows = [toList("QWERTYUIOP".lower()),toList("ASDFGHJKL".lower()),toList("ZXCVBNM".lower())]
    shift_keys3rows = [toList("QWERTYUIOP"),toList("ASDFGHJKL"),toList("ZXCVBNM")]
    def __init__(self):
        OSKeyboard.__init__(self,"English",EnglishKeyboard.keys3rows,EnglishKeyboard.shift_keys3rows)

class TamilKeyboard(OSKeyboard):
    special = "புள்ளி"
    space = "வெளி"
    pulli = "் "
    keys3rows = [toList("ஆஈஊஏளறனடணசஞ"),toList("அஇஉஐஎகபமதநய"),["ஔ","ஓ","ஒ","வ","ங","ல","ர","ழ"]]
    shift_keys3rows = [["௧","௨","௩","௪","௫","௬","௭","௮","௯","௦","௰"],
                       ["ஃ","ஸ","ஷ","ஜ","ஹ","க்ஷ","ஶ்ரீ","ஶ","ௐ","௱","௲"],
                       ["௳","௴","௵","௶","௷","௸","௹","௺"]]
    def __init__(self):
        OSKeyboard.__init__(self,"Tamil",TamilKeyboard.keys3rows,TamilKeyboard.shift_keys3rows)

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

    def build_kbd(self,numerickbd=False):
        self.clear_parent()
        self.activekbd.build_widget(self.parent_box,self.ed,numerickbd)
        self.setup_toggle_hooks()

    ############ logic functions ###########
    def setup_toggle_hooks(self):
        switch_btn = self.activekbd.keys3rows_btns[-1][1]
        switch_btn.connect("clicked", JointKeyboard.callback,self)

        num_btn = self.activekbd.keys3rows_btns[-1][0]
        num_btn.connect("clicked", JointKeyboard.numerickbd_callback,self)
        shift_btn = self.activekbd.keys3rows_btns[-2][0]
        shift_btn.connect("clicked", JointKeyboard.shift_callback,self)
        if self.activekbd.numericmode():
            shift_btn.hide()

    def clear_parent(self):
        kids = self.parent_box.get_children()
        for key_rows in kids[1:]:
            key_rows.destroy()

    def switch_kbd(self):
        if self.activekbd.numericmode():
            return

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

    @staticmethod
    def shift_callback(*args):
        widget = args[0]
        instance = args[1]
        instance.activekbd.toggle_shift_mode()
        instance.build_kbd(numerickbd=False)
        pass

    @staticmethod
    def numerickbd_callback(*args):
        widget = args[0]
        instance = args[1]
        instance.build_kbd(numerickbd=True)
        return
