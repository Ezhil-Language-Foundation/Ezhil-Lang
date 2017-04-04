#!/usr/bin/env python
##This Python file uses the following encoding: utf-8
##
## (C) 2017 Muthiah Annamalai,
## XML

from __future__ import print_function
from xml.dom.minidom import parse
import sys
import os
import tamil
import codecs
import re
import pprint
from xml.dom.minidom import parse as xml_parse

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, GLib, Pango
from syntaxhighlighing import EzhilSyntaxHighlightingEditor

# represents DTD of our XML
class XMLtoDocVisitor:
    def __init__(self):
        self.dom = None
        pass

    def visit(self,dom_in):
        for child in dom_in.childNodes:
            #print(dir(child))
            name = child.nodeName
            if name == "chapter":
                self.visit_chapter(child)
                self.visit(child)
            elif name == "section":
                self.visit_section(child)
                self.visit(child)
            elif name == "list": #terminal node
                self.visit_list(child)
            elif name == "code": #terminal node
                self.visit_code(child)
            else: #child.name == "text": #terminal node
                self.visit_text(child)

    def visit_chapter(self,*args):
        raise NotImplementedError()

    def visit_section(self,*args):
        raise NotImplementedError()

    def visit_code(self,*args):
        raise NotImplementedError()

    def visit_text(self,text):
        raise NotImplementedError()

    def visit_list(self,*args):
        raise NotImplementedError()

# class worries about the layouts and Gtk ops
class DocLayoutWidgetActions(object,XMLtoDocVisitor):
    def __init__(self):
        object.__init__(self)
        XMLtoDocVisitor.__init__(self)
        self.highlighter = EzhilSyntaxHighlightingEditor()
        self.highlighter.append_mode = True
        self.chapters = {}
        self.tag = {}
        self.pageno = 0
        self.default_font = "Sans 18"
        self.default_font_title = "Sans 24"
        self.textbuffer = None
        self.layoutpos = {"title":u"","section":0}

    def build_tags(self,textbuffer):
        self.tag["comment"]  = textbuffer.create_tag("comment",
            weight=Pango.Weight.SEMIBOLD,foreground="red",font=self.default_font)
        self.tag["code"]  = textbuffer.create_tag("code",
            style=Pango.Style.ITALIC,font=self.default_font,foreground="green")
        # use for chapter title
        self.tag["title"]  = textbuffer.create_tag("keyword",
            weight=Pango.Weight.BOLD,foreground="blue",font=self.default_font_title)
        # use for text/section tags
        self.tag["text"] = textbuffer.create_tag("text",font=self.default_font,foreground="black")
        self.tag["literal"]  = textbuffer.create_tag("literal",
            style=Pango.Style.ITALIC,font=self.default_font,foreground="green")
        self.tag["operator"] = textbuffer.create_tag("operator",
            weight=Pango.Weight.SEMIBOLD,font=self.default_font,foreground="olive")
        self.tag["found"] = textbuffer.create_tag("found",font=self.default_font,
            background="yellow")
        self.tag["list"]  = textbuffer.create_tag("list",
            weight=Pango.Weight.SEMIBOLD,font=self.default_font,foreground="red")
        self.tag["pass"]  = textbuffer.create_tag("pass",
            weight=Pango.Weight.SEMIBOLD,font=self.default_font,foreground="green")

        self.highlighter.tag_comment = self.tag["comment"]
        self.highlighter.tag_keyword  = self.tag["title"]
        self.highlighter.tag_literal = self.tag["literal"]
        self.highlighter.tag_operator = self.tag["operator"]
        self.highlighter.tag_found = self.tag["found"]
        self.highlighter.tag_text = self.tag["text"]
        self.highlighter.tag_fail = self.tag["list"]
        self.highlighter.tag_pass = self.tag["pass"]


    def visit_chapter(self,*args):
        child = args[0]
        title = u"%d) "%self.pageno + child.getAttribute("title")+u"\n"
        self.layoutpos["title"]=title
        print("Chapter => %s"%title)
        self.append_text_with_tag(title,self.tag["title"])

    def visit_section(self,*args):
        child = args[0]
        self.layoutpos["section"] += 1
        print("Section => %s"%str(child))
        self.append_text_with_tag(u"_"*100+u"\n",self.tag["text"])
        self.append_text_with_tag(u"பிரிவு %d\n"%self.layoutpos["section"],self.tag["found"])

    def visit_code(self,*args):
        child = args[0]
        print("Code => %s"%str(child))
        ref_text = None
        for node in child.childNodes:
            if node.nodeType == node.TEXT_NODE:
                ref_text = node
                break
        if ref_text:
            self.highlighter.run_syntax_highlighting(ref_text.data)
        pass

    def visit_text(self,text):
        child = text
        print("Text => %s"%str(child))
        self.append_text_with_tag(child.data,self.tag["text"])

    def visit_list(self,*args):
        child = args[0]
        print("List => %s"%str(child))
        ref_text = None
        for node in child.childNodes:
            if node.nodeType == node.TEXT_NODE:
                ref_text = node
                break
        if ref_text:
            idx = 0
            for _,line in enumerate(re.split("\n+",ref_text.data.strip())):
                line = line.strip()
                line = re.sub("^\*","    ",line)
                if len(line) < 1:
                    continue
                idx = idx + 1
                self.append_text_with_tag(u"    %d)"%idx+line+u"\n",self.tag["list"])
        pass

    def append_text_with_tag(self,text,tag):
        textbuffer = self.textbuffer
        self.highlighter.textbuffer = self.textbuffer
        textbuffer.insert_at_cursor( text )
        n_end = textbuffer.get_end_iter()
        n_start = textbuffer.get_iter_at_offset(textbuffer.get_char_count()-len(text))
        textbuffer.apply_tag(tag,n_start,n_end)
        return

    def render_toc_page(self):
        pass

    def render_page(self,pageno,textbuffer):
        if len(self.tag.keys()) == 0:
            self.build_tags(textbuffer)
        self.pageno = pageno
        self.textbuffer = textbuffer

        # reset
        self.layoutpos = {"title":u"","section":0}
        self.textbuffer.set_text(u"")

        if pageno == 0:
            return self.render_toc_page()

        dom = self.chapters[pageno]['dom']
        self.visit(dom)
        print("==========END VISITOR=======")
        with codecs.open(self.chapters[pageno]['file'],'r','utf-8') as fp:
            data = fp.read()

        # str_val = dom.getElementsByTagName("chapter")[0].getAttribute("title")
        # print("Title => %s"%str_val)
        # textbuffer.set_text( str_val )
        # n_end = textbuffer.get_end_iter()
        # n_start = textbuffer.get_iter_at_offset(textbuffer.get_char_count()-len(str_val))
        # textbuffer.apply_tag(self.tag["title"],n_start,n_end)

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
        self.textview.set_editable(False)
        self.textview.set_cursor_visible(True)

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
        self.book.render_page(self.page,self.textbuffer)
        return True

    def on_selection_button_clicked(self, widget):
        return True

if __name__ == u"__main__":
    win = DocBrowserWindow()
    Gtk.main()
