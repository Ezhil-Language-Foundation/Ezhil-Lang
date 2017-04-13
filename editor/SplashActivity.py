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
    LICENSE_NOTE = u"""

    எழில் - தமிழ் கணினி மொழி
    தமிழில் நிரல்படுத்தி கணிமை பழகுவோம்!
    (c) 2009 - 2017 எழில் மொழி அறக்கட்டளை
    =========================================================
    The code for Ezhil Language software is distributed under the following GPLv3 license
    The associated packages with Ezhil are distributed under respective open-source licenses
    documented under 'Help > About' menu.
    
    Copyright (C) 2007-2017, Muthiah Annamalai and other contributors

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
        self.display_tinylicense()
        follow_action()
        return

    def display_tinylicense(self):
        window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        window.set_default_size(100,150) #vanishingly small size
        window.connect("delete-event",Gtk.main_quit)
        dialog = Gtk.MessageDialog(window, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK,u"எழில் - தமிழ் கணினி மொழி")
        dialog.format_secondary_text(SplashActivity.LICENSE_NOTE)
        dialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        response = dialog.run()
        dialog.destroy() #OK or Cancel don't matter
