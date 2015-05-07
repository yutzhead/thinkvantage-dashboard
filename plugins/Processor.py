#!/usr/bin/python3
from gi.repository import Gtk
from plugins.utils import TextRow, PercentageRow, f_g_c

import subprocess
import re

class Processor():
    def __init__(self):
        # Perform basic initialization
        self.autoupdate = 3

    def getHeader(self):
        # Return a title as shown in the sidebar
        return 'Processor'

    def shouldDisplay(self):
        # Perform checks whether this plugin is available on this ThinkPad
        return True

    def _parseShell(self, cmd, filter=None):
        toReturn = {}
        output = subprocess.check_output(cmd, shell=True).decode('utf-8')

        for line in output.split('\n'):
            if not filter or filter in line:
                try:
                    info = line.split(':')
                    toReturn[info[0].strip()] = info[1].strip()
                except: continue

        return toReturn

    def _lscpu(self):
        return self._parseShell('lscpu')

    def _fanTemps(self):
        return self._parseShell('sensors', filter='fan')

    def _coreTemps(self):
        return self._parseShell('sensors', filter='Core')

    def getListboxRows(self):
        # Return a list of GtkWidgets for the main area
        yield Gtk.Label()

        lscpu = self._lscpu()

        yield TextRow('Model name', lscpu['Model name'].split(' @')[0], plain=True)
        yield TextRow('Number of cores', int(lscpu['Core(s) per socket'])*int(lscpu['Socket(s)']), plain=True)
        yield TextRow('Threads per core', int(lscpu['Thread(s) per core']), plain=True)

        try:
            yield TextRow('L3 cache', float(lscpu['L3 cache'][:-1])/1024, frmt='%.fM', plain=True)
        except:
            yield TextRow('L2 cache', float(lscpu['L2 cache'][:-1])/1024, frmt='%.fM', plain=True)

        yield TextRow('Architecture', lscpu['Architecture'], plain=True)

        for key,value in self._fanTemps().items():
            yield TextRow('Speed '+key, value, plain=True)

        re_temp = re.compile('(.*?)°C  \(high = (.*?)°C, crit = (.*?)°C\)')
        temps = self._coreTemps()
        for key in sorted(temps.keys()):
            try:
                tmps = re_temp.search(temps[key]).groups()
                yield TextRow(
                    'Temperature '+key, "%.0f°C (%.0f°C critical)" % (float(tmps[0]), float(tmps[2])),
                    plain=True
                )
            except:
                yield TextRow('Temperature '+key, value, plain=True)


        yield PercentageRow('CPU frequency',
                (float(lscpu['CPU MHz'])-float(lscpu['CPU min MHz']))/(float(lscpu['CPU max MHz'])-float(lscpu['CPU min MHz'])),
                "%.0f MHz (%.0f MHz max)" % (float(lscpu['CPU MHz']), float(lscpu['CPU max MHz']))
        )
