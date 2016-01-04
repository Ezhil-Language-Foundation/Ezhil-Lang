import gi
gi.require_version('Gtk','3.0')

from gi.repository import Gtk

class Handler:
    def onDeleteWindow(self, *args):
        Gtk.main_quit(*args)

    def onButtonPressed(self, button):
        print("Hello World!")

def example():
    builder = Gtk.Builder()
    builder.add_from_file("example.glade")
    builder.connect_signals(Handler())

    window = builder.get_object("window1")
    window.show_all()

builder = Gtk.Builder()
builder.add_from_file("editor.glade")

def abt_dlg_closer(abt_dlg,event):
    abt_dlg.hide()

def show_about_status(*args):
    global builder
    abt_menu = args[0]
    abt_dlg = builder.get_object("ezhilAboutDialog")
    #Parent = builder.get_object("ezhilEditorWindow"))
    abt_dlg.show_all()
    close_btn = builder.get_object("aboutdialog-action_area1")
    abt_dlg.connect("response",abt_dlg_closer)
    return True

window = builder.get_object("ezhilEditorWindow");
# connect abt menu and toolbar item
abt_menu = builder.get_object("aboutMenuItem")
abt_menu.connect("activate",show_about_status)

abt_btn = builder.get_object("AboutBtn")
abt_btn.connect("clicked",show_about_status)
window.show_all()

Gtk.main()
