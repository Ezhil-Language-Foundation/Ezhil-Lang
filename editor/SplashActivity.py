#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## (C) 2017 Ezhil Language Foundation
## Licensed under GPL Version 3

from __future__ import print_function
import sys
import time
import gi
PYTHON3 = (sys.version[0] == '3')
if PYTHON3:
    unicode = str

gi.require_version('Gtk','3.0')
from gi.repository import Gtk, GObject

class SplashActivity:
    """
        எழில் - தமிழ் கணினி மொழி
        தமிழில் நிரல்படுத்தி கணிமை பழகுவோம்!
        (c) 2009 - 2017 எழில் மொழி அறக்கட்டளை
    """
    def __init__(self,follow_action):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("res/editor.glade")
        splash = self.builder.get_object("splashWindow")
        splash.set_decorated(False)
        splash.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        splash.show()
        secs_start = time.time()
        while Gtk.events_pending():
            Gtk.main_iteration()
        GObject.timeout_add(2500,Gtk.main_quit)
        Gtk.main()
        splash.destroy()
        follow_action()
