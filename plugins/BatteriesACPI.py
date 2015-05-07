#!/usr/bin/python3
from gi.repository import Gtk
from plugins.utils import TextRow, PercentageRow, f_g_c

class BatteryACPI():
    def __init__(self, battery):
        self.bat = battery
        self.autoupdate = 5

    def getHeader(self):
        return 'Battery'

    def shouldDisplay(self):
        try:
            return int(f_g_c('/sys/class/power_supply/BAT%s/present' % self.bat)) == 1
        except:
            return False

    def getRows(self):
        yield Gtk.Label()

        yield TextRow('Manufacturer', '/sys/class/power_supply/BAT%s/manufacturer' % self.bat, True)
        yield TextRow('Model', '/sys/class/power_supply/BAT%s/model_name' % self.bat)

        yield TextRow('Cycle Count', '/sys/class/power_supply/BAT%s/cycle_count' % self.bat)

        yield TextRow('Current state', '/sys/class/power_supply/BAT%s/status' % self.bat, True)
        stateVal = f_g_c('/sys/class/power_supply/BAT%s/status' % self.bat)
        #if stateVal == 'Charging':
        #    yield TextRow('Remainging charging time',
        #        '/sys/devices/platform/smapi/BAT%s/remaining_charging_time' % self.bat,
        #        frmt='%s minutes'
        #    )
        #elif stateVal == 'idle':
        #    pass
        #else:
        #    yield TextRow('Remainging running time',
        #        '/sys/devices/platform/smapi/BAT%s/remaining_running_time_now' % self.bat,
        #        frmt='%s minutes'
        #    )
        try:
            designCapacityVal = int(int(f_g_c('/sys/class/power_supply/BAT%s/energy_full_design' % self.bat))/1000)
            lastFullCapacityVal = int(int(f_g_c('/sys/class/power_supply/BAT%s/energy_full' % self.bat))/1000)
            remainingCapacityVal = int(int(f_g_c('/sys/class/power_supply/BAT%s/energy_now' % self.bat))/1000)
        except:
            designCapacityVal = int(int(f_g_c('/sys/class/power_supply/BAT%s/capacity_full_design' % self.bat))/1000)
            lastFullCapacityVal = int(int(f_g_c('/sys/class/power_supply/BAT%s/capacity_full' % self.bat))/1000)
            remainingCapacityVal = int(int(f_g_c('/sys/class/power_supply/BAT%s/capacity_now' % self.bat))/1000)

        remainingPercentVal = float(remainingCapacityVal)/float(lastFullCapacityVal)

        yield PercentageRow('Battery Health',
            float(lastFullCapacityVal)/float(designCapacityVal),
            "%s of %s mWh" % (lastFullCapacityVal, designCapacityVal)
        )

        yield PercentageRow('Remaining Charge',
            float(remainingPercentVal),
            "%s of %s mWh" % (remainingCapacityVal, lastFullCapacityVal)
        )

        voltageVal = int(f_g_c('/sys/class/power_supply/BAT%s/voltage_now' % self.bat))
        yield PercentageRow('Battery Voltage',
            float((voltageVal/1000)-10200)/2400.0,
            "%s mV" % int(voltageVal/1000)
        )
