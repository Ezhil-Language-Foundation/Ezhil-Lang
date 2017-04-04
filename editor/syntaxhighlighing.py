#!/usr/bin/env python
##This Python file uses the following encoding: utf-8
##
## (C) 2016-2017 Muthiah Annamalai,
## Licensed under GPL Version 3
from __future__ import print_function
import sys

PYTHON3 = (sys.version[0] == '3')
if PYTHON3:
    unicode = str
import ezhil
import gi

gi.require_version('Gtk','3.0')
from gi.repository import Gtk, GObject, GLib, Pango

class Tokenizer:
    # given a piece of text figure out if it is a number, string-literal or
    # a keyword or just plain old text
    def __init__(self):
        self.lexer = ezhil.EzhilLex()

    def tokenize(self,chunk):
        self.lexer.reset()
        self.lexer.tokenize(chunk)
        self.lexer.tokens.reverse()
        return self.lexer.tokens

class EzhilSyntaxHighlightingEditor(object):
    def __init__(self):
        self.append_mode = False
        self.textbuffer = None
        self.tag_comment = None
        self.tag_keyword  = None
        self.tag_literal = None
        self.tag_operator = None
        self.tag_found = None
        self.tag_text = None
        self.tag_fail = None
        self.tag_pass = None

    def refresh_tags(self):
        if self.tag_text:
            for tags in [self.tag_comment, self.tag_keyword, self.tag_literal, self.tag_operator, self.tag_text, self.tag_found, self.tag_fail, self.tag_pass]:
                if tags: tags.set_property("font",self.default_font)
            return

        self.tag_comment  = self.textbuffer.create_tag("comment",
            weight=Pango.Weight.SEMIBOLD,foreground="red",font=self.default_font)
        self.tag_keyword  = self.textbuffer.create_tag("keyword",
            weight=Pango.Weight.BOLD,foreground="blue",font=self.default_font)
        self.tag_literal  = self.textbuffer.create_tag("literal",
            style=Pango.Style.ITALIC,font=self.default_font,foreground="green")
        self.tag_operator = self.textbuffer.create_tag("operator",
            weight=Pango.Weight.SEMIBOLD,font=self.default_font,foreground="olive")
        self.tag_text = self.textbuffer.create_tag("text",font=self.default_font,foreground="black")
        self.tag_found = self.textbuffer.create_tag("found",font=self.default_font,
            background="yellow")

    def apply_comment_syntax_highlighting(self,c_line):
        syntax_tag = self.tag_comment
        self.textbuffer.insert_at_cursor( c_line )
        self.textbuffer.insert_at_cursor(u"\n")
        n_end = self.textbuffer.get_end_iter()
        n_start = self.textbuffer.get_iter_at_offset(self.textbuffer.get_char_count()-1-len(c_line))
        self.textbuffer.apply_tag(syntax_tag,n_start,n_end)

    def run_syntax_highlighting(self,text,bounds=None):
        EzhilToken = ezhil.EzhilToken
        if not bounds:
            start,end = self.textbuffer.get_bounds()
        else:
            start,end = bounds
        if not self.append_mode:
            self.textbuffer.delete(start,end)
        lines = text.split(u"\n")
        lexer = Tokenizer()
        for line in lines:
            comment_line = line.strip()
            if comment_line.startswith(u"#"):
                self.apply_comment_syntax_highlighting(comment_line)
                continue
            idx_comment_part = comment_line.find("#")
            if idx_comment_part != -1:
                line_alt = comment_line[0:idx_comment_part]
                comment_line = comment_line[idx_comment_part:]
            else:
                line_alt = line
                comment_line = None
            line = line_alt
            lexemes = lexer.tokenize(line)
            for lexeme in lexemes:
                is_string = False
                tok = lexeme.kind
                is_keyword = False
                if unicode(lexeme.val) in [u"உள்ளடக்கு",u"பின்கொடு",u"பதிப்பி",u"ஒவ்வொன்றாக",u"@",u"இல்",u"நிறுத்து"] or EzhilToken.is_keyword(tok):
                    is_keyword = True
                    syntax_tag = self.tag_keyword
                elif EzhilToken.is_id(tok):
                    syntax_tag = self.tag_operator
                elif EzhilToken.is_number(tok):
                    syntax_tag = self.tag_literal
                elif EzhilToken.is_string(tok):
                    is_string = True
                    syntax_tag = self.tag_literal
                else:
                    syntax_tag = self.tag_text
                m_start = self.textbuffer.get_insert()

                if is_keyword:
                     lexeme_val = lexeme.val + u" "
                elif EzhilToken.is_number(lexeme.kind):
                    lexeme_val = unicode(lexeme.val)
                elif is_string:
                     lexeme_val = u"\""+lexeme.val.replace(u"\n",u"\\n")+u"\""
                else:
                     lexeme_val = lexeme.val
                self.textbuffer.insert_at_cursor( lexeme_val )
                n_end = self.textbuffer.get_end_iter()
                n_start = self.textbuffer.get_iter_at_offset(self.textbuffer.get_char_count()-len(lexeme_val))
                self.textbuffer.apply_tag(syntax_tag,n_start,n_end)
                #self.textbuffer.insert_at_cursor(u" ")
            if comment_line:
                self.apply_comment_syntax_highlighting(u" "+comment_line)
                continue
            self.textbuffer.insert_at_cursor(u"\n")