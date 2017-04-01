#!/usr/bin/env python
##This Python file uses the following encoding: utf-8
##
## (C) 2017 Muthiah Annamalai,
## XML

from __future__ import print_function
from xml.dom.minidom import parse
import sys
import os
import glob
import tamil
import codecs
import re
import pprint
from xml.dom.minidom import parse as xml_parse

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# class worries about the layouts and Gtk ops
class DocLayoutWidgetActions(object):
    def __init__(self):
        object.__init__(self)
        self.chapters = {}

    def render_page(self,pageno,textview,textbuffer):
        dom = self.chapters[pageno]['dom']
        with codecs.open(self.chapters[pageno]['file'],'r','utf-8') as fp:
            data = fp.read()
        textbuffer.set_text( data )
        return True

    def update_toc(self,box,parent):
        for pos,chapter in self.chapters.items():
            btn = Gtk.Button(u"%d. %s"%(pos,chapter['title']))
            btn.connect('clicked',parent.on_navigate_to,chapter['title'],pos)
            box.pack_start(btn,True,True,0)
        return True


# class contains the books
class XMLtoDoc(DocLayoutWidgetActions):
    def __init__(self,chapters_in_order):
        DocLayoutWidgetActions.__init__(self)
        self.chapters_in_order = chapters_in_order
        for idx,chapter in enumerate(self.chapters_in_order):
            dom = xml_parse(chapter)
            title = dom.getElementsByTagName("chapter")[0].getAttribute("title")
            self.chapters[idx+1] = {'dom':dom,'title':title,'file':chapter}
        self.build_index()
        self.build_toc()

    def pages(self):
        return len(self.chapters)+1
    def build_index(self):
        pass

    def build_toc(self):
        pass

class DocBrowserWindow(object):
    def __init__(self,ref_editor=None):
        object.__init__(self)
        self.builder = Gtk.Builder()
        title="Ezhil Help Browser"

        book_chapters = ['ch1.xml', 'ch2.xml', 'ch3.xml', 'ch4.xml', 'ch5.xml', 'ch6.xml', 'ch7.xml', 'ch8.xml','appendix.xml']
        self.book = XMLtoDoc( map(lambda x: os.path.join('xmlbook',x),book_chapters) )
        self.page = 0 #TOC/HOME

        self.builder.add_from_file("res/helper.glade")

        self.window = self.builder.get_object("appEzhilHelpBook")
        self.window.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

        self.tocbox = self.builder.get_object("boxToc")
        self.book.update_toc(self.tocbox,self)

        self.textview = self.builder.get_object("textview1")
        self.textbuffer = self.textview.get_buffer()

        self.btn_next = self.builder.get_object("btnNext")
        self.btn_next.connect("clicked",lambda arg: self.on_navigate(arg,'->'))
        self.btn_prev = self.builder.get_object("btnPrev")
        self.btn_prev.connect("clicked",lambda arg: self.on_navigate(arg,'<-'))
        self.btn_home = self.builder.get_object("btnHome")
        self.btn_home.connect("clicked",lambda arg: self.on_navigate(arg,'x'))
        if not ref_editor:
            self.window.connect("delete-event", Gtk.main_quit)
        self.window.show_all()

    def on_navigate(self,widget,direction):
        if direction == '->':
            print(u"forward ")
            if self.page < self.book.pages():
                self.page += 1
        elif direction == '<-':
            print(u"backward ")
            if self.page >= 1:
                self.page -= 1
        elif direction == 'x':
            print(u"home")
            self.page = 0
        print("current page -> %d"%self.page)
        self.render_page()
        return True

    def on_navigate_to(self,widget,chapter_name,pos):
        print(u'Navigating to -> %s @ pos = %d'%(chapter_name,pos))
        self.page = pos
        self.render_page()
        return True

    def render_page(self):
        self.book.render_page(self.page,self.textview,self.textbuffer)
        return True

    def on_selection_button_clicked(self, widget):
        return True

if __name__ == u"__main__":
    win = DocBrowserWindow()
    Gtk.main()
