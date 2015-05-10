from gi.repository import Gtk, Gdk, Clutter, GtkClutter, GLib
from threading import Lock
import subprocess
import re
import math

from plugins.utils import f_g_c

class TransparentEmbed(GtkClutter.Embed):
    def __init__(self):
        GtkClutter.Embed.__init__(self)
        self.props.expand = False
        self.props.hexpand = True

        self._canvas = Clutter.Canvas()
        self.get_stage().props.content = self._canvas

        def draw(canvas, cairocontext, width, height):
            Gtk.render_background(
                self.get_toplevel().get_style_context(),
                cairocontext,
                0, 0,
                width, height
            )
            return True
        self._canvas.connect('draw', draw)

        def realize(widget):
            self.get_stage().props.content = self._canvas
        self.connect('realize', realize)

        def size_allocate(widget, size):
            self._canvas.set_size(size.width, size.height)
            self._evaluateGeometry(size.width)
        self.connect('size-allocate', size_allocate)

        def style_updated(widget):
            self.get_stage().props.content.invalidate()
        self.connect('style-updated', style_updated)

class FancyMemoryRow():
    def __init__(self, meminfo):
        self.embed = TransparentEmbed()
        self.stage = self.embed.get_stage()
        self.embed._evaluateGeometry = self._evaluateGeometry
        self.dimms = []
        self.empty = []
        self.actors = []

        self.max_width = 0
        for r in range(math.ceil(len(meminfo)/2)):
            try: mi = meminfo[(r*2):(r*2)+2]
            except: mi = meminfo[(r*2):]

            for i in range(len(mi)):
                m = mi[i]
                l = Gtk.Label()

                l.set_justify(Gtk.Justification.CENTER)
                l.set_name('MemoryLabel')

                if m[0] == 'No Module Installed':
                    l.set_text("\n\nEmpty\n\n")
                    l.set_name('MemoryLabelEmpty')

                    actor = GtkClutter.Actor(contents=l)
                    actor.set_y(15+(130*r))
                    actor.set_opacity(0)
                    self.empty.append(actor)

                else:
                    l.set_text("\n%s %s %s\nManufacturer: %s\nModel: %s\n" % (m[0], m[2], m[3], m[4], m[5].strip()))
                    l.set_name('MemoryLabel')

                    actor = GtkClutter.Actor(contents=l)
                    actor.set_y(-50-(125*(int(len(meminfo)/2)-r)))
                    actor.set_rotation_angle(Clutter.RotateAxis.X_AXIS,-5.0)

                    self.dimms.append([actor, r])

                actor.set_pivot_point(0.0,1.0)

                self.actors.append([actor,r,i])
                self.stage.add_actor(actor)

        self.embed.props.height_request = (128*math.ceil(len(meminfo)/2))

    def _evaluateGeometry(self, topWidth=0):
        for a in self.actors:
            w = a[0].get_width()
            if self.max_width < w:
                self.max_width = w+9

        if topWidth > (self.max_width*2)+25:
            topAdder = (topWidth-(self.max_width*2)+25)/2
        else:
            topAdder = 0

        for a in self.actors:
            a[0].set_width(self.max_width)
            a[0].set_x(((self.max_width+25)*a[2])+topAdder-25)

    def animate(self):
        self.lock.acquire()
        for d in self.dimms:
            d[0].animatev(Clutter.AnimationMode.EASE,
                           1000, ['y'], [15+(130*d[1])])
        def run():
            for d in self.dimms:
                d[0].animatev(Clutter.AnimationMode.EASE,
                           1000, ['rotation-angle-x'], [0.0])
            def run():
                for e in self.empty:
                    e.animatev(Clutter.AnimationMode.EASE,
                            1000, ['opacity'], [255])
            GLib.timeout_add(525,run)
            GLib.timeout_add(1100,self.lock.release)
        GLib.timeout_add(1100,run)

class Memory():
    def __init__(self):
        # Perform basic initialization
        self.autoupdate = -1 # Reloads data via getListboxRows every self.autoupdate seconds
        self.lock = Lock()

    def getHeader(self):
        # Return a title as shown in the sidebar
        return 'Memory'

    def shouldDisplay(self):
        # Perform checks whether this plugin is available on this ThinkPad
        return True

    def _getMemInfo(self):
        try:
            if self.meminfo: return
        except:
            memInfo = subprocess.check_output('pkexec dmidecode -t memory', shell=True).decode('utf-8')
            RE_RAM = re.compile(r'\tSize: (.*?)\n.*?Form Factor: (.*?)\n.*?Type: (.*?)\n.*?Speed: (.*?)\n.*?Manufacturer: (.*?)\n.*?Part Number: (.*?)\n', re.DOTALL)
            RE_MAXRAM = re.compile(r'Maximum Capacity: (.*?)\n')

            self.meminfo = [self._parseBytes(RE_MAXRAM.search(memInfo).group(1))]
            self.meminfo.append(RE_RAM.findall(memInfo))

    def _parseBytes(self, bytes):
        try:
            value, suffix = bytes.split(' ')
            return int(value)*(1024**['B','KB','MB','GB','TB','PB','EB','ZB','YB'].index(suffix))
        except: return bytes

    def _sizeof_fmt(self, num, suffix='B'):
        for unit in ['','K','M','G','T','P','E','Z']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Y', suffix)

    def getRows(self):
        if f_g_c('/sys/devices/virtual/dmi/id/product_version').find('ThinkPad') >= 0:
            color = b'white'
        else:
            color = b'black'

        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(b"""
            #MemoryLabel {
                color: """+color+b""";
                border-style: solid;
                border-width: 1px;
                border-radius: 5px;
                border-color:"""+color+b""";
                padding: 0px 4px;
            }
            #MemoryLabelEmpty {
                color: darkgray;
                border-style: solid;
                border-width: 1px;
                border-radius: 5px;
                border-color:darkgray;
                padding: 0px 4px;
            }
        """)

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Return a list of GtkWidgets for the main area
        yield Gtk.Label()
        self._getMemInfo()
        self.installedMem = 0
        for m in self.meminfo[1]:
            try:
                self.installedMem += self._parseBytes(m[0])
            except: pass

        meminfo = self.meminfo[1]

        e = FancyMemoryRow(meminfo)
        e.lock = self.lock
        yield e.embed
        yield Gtk.Label()

        GLib.idle_add(e.animate)

        l = Gtk.Label('This ThinkPad supports up to %s of memory, %s of which are installed.' % (self._sizeof_fmt(self.meminfo[0]), self._sizeof_fmt(self.installedMem)))
        l.props.hexpand = True

        yield l


# Add an instance of the plugin for auto-discovery with priority 99
#PLUGINS.append((99, MyPlugin()))
