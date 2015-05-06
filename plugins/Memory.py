from gi.repository import Gtk, Gdk
import subprocess
import re

class Memory():
    def __init__(self):
        # Perform basic initialization
        self.autoupdate = -1 # Reloads data via getListboxRows every self.autoupdate seconds

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
            RE_RAM = re.compile(r'Size: (.*?)\n.*?Form Factor: (.*?)\n.*?Type: (.*?)\n.*?Speed: (.*?)\n.*?Manufacturer: (.*?)\n.*?Part Number: (.*?)\n', re.DOTALL)
            RE_MAXRAM = re.compile(r'Maximum Capacity: (.*?)\n')
            self.meminfo = [self._parseBytes(RE_MAXRAM.search(memInfo).group(1))]

            self.meminfo.append(RE_RAM.findall(memInfo))

    def _parseBytes(self, bytes):
        vals = [('KB', 1024),('MB', 1024*1024),('GB', 1024*1024*1024)]
        suffix = bytes.split(' ')[1]
        value = int(bytes.split(' ')[0])
        for v in vals:
            if suffix == v[0]:
                return value * v[1]
        return value

    def _sizeof_fmt(self, num, suffix='B'):
        for unit in ['','K','M','G','T','P','E','Z']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Y', suffix)

    def getListboxRows(self):
        # Return a list of GtkWidgets for the main area
        rows = [Gtk.Label()]
        self._getMemInfo()
        self.installedMem = 0

        meminfo = self.meminfo[1]

        box = Gtk.Table(int(len(self.meminfo)/2), 16, True)
        box.set_row_spacings(18)
        box.set_col_spacings(18)

        for r in range(int(len(meminfo)/2)):
            try: mi = meminfo[(r*2):(r*2)+2]
            except: mi = meminfo[(r*2):]

            for i in range(len(mi)):
                m = mi[i]
                l = Gtk.Label()

                l.set_justify(Gtk.Justification.CENTER)
                l.set_name('MemoryLabel')

                if m[0] == 'No Module Installed':
                    l.set_text("\n\nEmpty\n\n")
                else:
                    l.set_text("\n%s %s %s\nManufacturer: %s\nModel: %s\n" % (m[0], m[2], m[3], m[4], m[5].strip()))
                    self.installedMem += self._parseBytes(m[0])

                if i % 2 == 0: box.attach(l, 1,6,r,r+1)
            else: box.attach(l, 6,11,r,r+1)
        rows.append(box)
        rows.append(Gtk.Label())

        box=Gtk.Table(1,16,True)
        box.attach(Gtk.Label('This ThinkPad supports up to %s of memory, of which %s are installed.' % (self._sizeof_fmt(self.meminfo[0]), self._sizeof_fmt(self.installedMem))), 1,11,0,1)
        rows.append(box)

        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(b"""
            #MemoryLabel {
                color: white;
                border-radius: 5px;
                border-style: solid;
                border-width: 1px;
                border-color:white;
                padding: 0px 4px;
                opacity: 0.9;
            }
        """)

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        return rows

# Add an instance of the plugin for auto-discovery with priority 99
#PLUGINS.append((99, MyPlugin()))
