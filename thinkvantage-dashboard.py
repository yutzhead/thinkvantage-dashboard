#!/usr/bin/python3
from gi.repository import Gtk, GLib, GObject, Gdk
import signal
import threading
import time
import sys
import os
import dbus
import dbus.service
import json
import subprocess

from dbus.mainloop.glib import DBusGMainLoop

from plugins.utils import f_g_c

from plugins.Batteries import Battery
from plugins.BatteriesACPI import BatteryACPI
from plugins.SystemOverview import SystemOverview
from plugins.Processor import Processor
from plugins.Memory import Memory

PLUGINS = [
    SystemOverview(),
    Processor(),
    Memory(),
    Battery(0) if Battery(0).shouldDisplay() else BatteryACPI(0),
    Battery(1) if Battery(1).shouldDisplay() else BatteryACPI(1)
]

loadPlugin = 0

DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus()
if bus.name_has_owner("org.tlp.thinkvantage"):
    proxy = bus.get_object('org.tlp.thinkvantage', '/org/tlp/thinkvantage')
    bringWindowToFocus = proxy.get_dbus_method('bringWindowToFocus', 'org.tlp.thinkvantage')
    loadPlugin = bringWindowToFocus()


class MainWindow(Gtk.Window):
    def _checkButton(self):
        hasThinkVantageButton = False
        settings = subprocess.check_output(
            'gsettings get org.gnome.settings-daemon.plugins.media-keys custom-keybindings', shell=True
        ).decode('utf-8')
        settings = json.loads(settings[settings.index('['):].replace('\'', '"'))

        for setting in settings:
            cmd = subprocess.check_output('gsettings get org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:'+setting+' binding', shell=True).decode('utf-8').strip()
            if cmd == "'Launch1'":
                hasThinkVantageButton = True
                break

        if not hasThinkVantageButton:
            settings.append('/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/ThinkVantage/')
            subprocess.check_output('gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings \'%s\'' % json.dumps(settings), shell=True)
            subprocess.check_output('gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/ThinkVantage/ name "ThinkVantage"', shell=True)
            subprocess.check_output('gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/ThinkVantage/ binding "Launch1"', shell=True)
            subprocess.check_output('gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/ThinkVantage/ command "python3 %s"' % os.path.realpath(__file__), shell=True)

            dialog = Gtk.MessageDialog(
                None, 0, Gtk.MessageType.INFO,
                Gtk.ButtonsType.OK,
                'ThinkVantage button',
            )
            dialog.format_secondary_text('ThinkVantage Dashboard has been added to your ThinkVantage button.')
            def run():
                dialog.run()
                dialog.destroy()
            GLib.idle_add(run)

    def _keyPress(self, widget, event):
        if Gdk.keyval_name(event.keyval) == 'Escape':
            Gtk.main_quit()

    def __init__(self, loadPlugin=0):
        self.dbusService = self.ButtonDBUSService()
        self.dbusService.window = self

        if f_g_c('/sys/devices/virtual/dmi/id/product_version').index('ThinkPad') >= 0:
            Gtk.Window.__init__(self, title='ThinkVantage Dashboard')
            self.set_wmclass ("ThinkVantage", "ThinkVantage")

            settings = Gtk.Settings.get_default()
            settings.set_property('gtk-application-prefer-dark-theme', True)

            style_provider = Gtk.CssProvider()
            style_provider.load_from_data(b'GtkWindow {background-color: #292929;} GtkWindow:backdrop {background-color:#2c2c2c}')
            Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(),
                style_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
        else:
            Gtk.Window.__init__(self, title='Laptop Dashboard')
            self.set_wmclass ("Laptop Dashboard", "Laptop Dashboard")

        self.set_icon_from_file(os.path.dirname(os.path.abspath(__file__))+'/icons/256x256.png')

        paned = Gtk.Paned()
        paned.set_position(200)
        self.add(paned)

        divisionBox = Gtk.ListBox()
        divisionBox.set_activate_on_single_click(True)
        divisionBox.connect('row-activated', self.rowClicked)
        self.connect('key-press-event', self._keyPress)
        paned.add1(divisionBox)

        for plugin in PLUGINS.copy():
            if not plugin.shouldDisplay():
                PLUGINS.remove(plugin)
                continue

            row = Gtk.ListBoxRow()
            label = Gtk.Label(plugin.getHeader())
            row.add(label)
            divisionBox.add(row)

        self.plugin = PLUGINS[loadPlugin]
        divisionBox.select_row(divisionBox.get_row_at_index(loadPlugin))

        box = Gtk.Box(spacing=12)
        paned.add2(box)
        self.listbox = Gtk.Grid()
        box.pack_start(self.listbox, True, True, 0)

        self.resize(850,450)
        self.activity_mode = False

        self.updateMainArea()

        if self.plugin.autoupdate > 0:
            GLib.timeout_add_seconds(self.plugin.autoupdate if self.plugin.autoupdate < 10 else 5, self.updateListbox)

        updateButtonThread = threading.Thread(target=self._checkButton)
        updateButtonThread.start()

    def rowClicked(self, listbox, row):
        self.plugin = PLUGINS[row.get_index()]
        self.updateMainArea()

        if self.plugin.autoupdate > 0:
            GLib.timeout_add_seconds(self.plugin.autoupdate if self.plugin.autoupdate < 10 else 5, self.updateListbox)

    def updateMainArea(self):
        children = self.listbox.get_children()
        for c in children:
            c.destroy()

        i = 0
        for row in self.plugin.getRows():
            self.listbox.attach(row,0,i,1,1)
            i = i+1

        self.show_all()
        if self.plugin.autoupdate < 0:
            return False
        return True

    def bringWindowToFocus(self):
        def run():
            self.present_with_time(int(time.time()))
        GLib.idle_add(run)

    class ButtonDBUSService(dbus.service.Object):
        def __init__(self):
            bus_name = dbus.service.BusName('org.tlp.thinkvantage', bus=dbus.SessionBus())
            dbus.service.Object.__init__(self, bus_name, '/org/tlp/thinkvantage')

        @dbus.service.method('org.tlp.thinkvantage')
        def bringWindowToFocus(self):
            Gtk.main_quit()
            return PLUGINS.index(self.window.plugin)

GObject.threads_init()
m = MainWindow(loadPlugin)
m.connect("delete-event", Gtk.main_quit)
m.show_all()

signal.signal(signal.SIGINT, signal.SIG_DFL)
Gtk.main()
