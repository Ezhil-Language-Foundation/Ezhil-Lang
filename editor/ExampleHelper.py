#!/usr/bin/env python
##This Python file uses the following encoding: utf-8
##
## (C) 2017 Muthiah Annamalai,
#  This code is released under public domain.
import os
import glob
import tamil
import codecs
import re
import pprint

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class ExampleDescription:
    data = {
'1_data_and_arithmetic_builtins':u'தொடக்க நிலை எண், கணித செயற்குறிகள் (arithmetic)', 
'2_conditional_if_statement':u'நிபந்தனை கட்டளைகள் (conditional)',
'3_for_while_loops':u'ஆக-முடி, வரை - மடக்கு வாக்கியம் (loop)',
'4_functions':u'நிரல்பாகம் - சார்புகள் (function)',
'5_recursive_functions':u'அடுக்கு நிரல்பாகம் - அடுக்கு சார்புகள் (recursive function)',
'6_data_structures':u'தரவமைப்பு வகைகள் (data structures)',
'7_advanced_concepts':u'மேல்நிலை பாடம் - கோப்பு, இயங்கு தளம்',
'examples':u'உதாரணங்கள்'}
 
# 'c:\\Users\\muthu\\devel\\ezhil-lang\\editor'
class ExampleDiscovery:
    # Build a DFS style flat-list of nested-directories looking for example files
    # on 03/30/17 we have over 177 examples.
    EXAMPLEROOT = u"examples"
    def __init__(self):
        self.examples = [[]]
        self.process(os.path.join(os.getcwd(),ExampleDiscovery.EXAMPLEROOT))
        #self.examples = filter(len,self.examples)
        #print("Total examples = %d"%sum(map(len,self.examples)))
        
    def process(self,fd):
        if os.path.isdir(fd):
            for f_or_d in glob.glob(os.path.join(fd,'*')):
                if os.path.isdir( f_or_d):
                    self.process( f_or_d )
                    self.examples.append([])
                else:
                    self.handlefile(f_or_d)
        else:
            self.handlefile(fd)

    def handlefile(self,fd):
        self.examples[-1].append(fd)

class ExampleBrowserWindow(Gtk.Window):
    def __init__(self,ref_editor=None):
        Gtk.Window.__init__(self, title="Ezhil Example Browser")
        self.set_size_request(300,350)
        try:
            self.set_icon_from_file("res/img/ezhil_square_2015_128px.png")
        except Exception as ie:
            pass
        self.set_title(u"எழில் : தமிழ் நிரலாக்க மொழி - உதாரணங்கள்")
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        #self.set_border_width(10)
        self.example_collector = ExampleDiscovery()
        self.ref_editor = ref_editor
        #Setting up the self.grid in which the elements are to be positionned
        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)
        self.add(self.grid)

        #Creating the ListStore model
        self.examplestore = Gtk.ListStore(str, str)
        with open("data.txt","w") as fp:
            pprint.pprint(self.example_collector.examples,fp)
        
        for direxample in self.example_collector.examples:
            if not ( type(direxample) is list ):
                continue
            if len(direxample) < 1:
                continue
            dirname = direxample[0].split(os.path.sep)    
            dirname = dirname[-2]
            self.examplestore.append([ExampleDescription.data.get(dirname,dirname).strip(),u'<folder/desc>'])
            for demoex in direxample:
                item = u'\t'+os.path.split(demoex)[-1]
                self.examplestore.append([item,demoex])

        #creating the treeview, making a model, and adding the columns
        self.treeview = Gtk.TreeView.new_with_model(self.examplestore)
        for i, column_title in enumerate([u"உதாரணங்கள்"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.treeview.append_column(column)
        
        self.buttons = list()
        prog_language = u"உதாரணம் காட்டு"
        button = Gtk.Button(prog_language)
        self.buttons.append(button)
        button.connect("clicked", self.on_selection_button_clicked)

        if not ref_editor:
            self.connect("delete-event", Gtk.main_quit)

        #setting up the layout, putting the treeview in a scrollwindow, and the buttons in a row
        self.scrollable_treelist = Gtk.ScrolledWindow()
        self.scrollable_treelist.set_property("vscrollbar-policy",Gtk.PolicyType.ALWAYS)
        self.scrollable_treelist.set_vexpand(False)
        self.treeview.set_property( 'enable-grid-lines', True)
        self.treeview.set_property('enable-tree-lines', True)
        self.treeview.set_property('enable-search', True)
        self.treeview.set_property('search-column', 0)
        self.treeview.set_enable_search(True)
        self.treeview.set_activate_on_single_click(True)
        self.treeview.set_rules_hint(True)
        self.treeview.connect("row-activated",lambda arg,b,c: self.on_selection_button_clicked(arg))
        self.treeview.connect("start-interactive-search",lambda arg: self.treeview_search(arg))
        self.grid.attach(self.scrollable_treelist, 0, 0, 7,8)
        self.grid.attach_next_to(self.buttons[0], self.scrollable_treelist, Gtk.PositionType.BOTTOM, 7, 1)
        self.scrollable_treelist.add(self.treeview)
        self.show_all()

    def language_filter_func(self, model, iter, data):
        """Tests if the language in the row is the one in the filter"""
        if self.current_filter_language is None or self.current_filter_language == "None":
            return True
        else:
            return model[iter][2] == self.current_filter_language

    def treeview_search(self,treeview):
        entry = self.treeview.get_search_entry()
        if entry:
            example_name = entry.get_text()
        else:
            return False
        print(example_name)
        return False

    def on_selection_button_clicked(self, widget):
        """Called on any of the button clicks"""
        tree_sel = self.treeview.get_selection()
        (tm, ti) = tree_sel.get_selected()
        example_name = tm.get_value(ti, 1)
        if example_name.find("<folder/desc>") >= 0:
            return True
        if self.ref_editor:
            self.ref_editor.show_example(example_name)
        else:
            print("example name => %s"%example_name)
        return True

if __name__ == u"__main__":
    win = ExampleBrowserWindow()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()
