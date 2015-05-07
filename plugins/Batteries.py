#!/usr/bin/python3
from gi.repository import Gtk
from plugins.utils import TextRow, PercentageRow, f_g_c

class Battery():
    def __init__(self, battery):
        self.bat = battery
        self.autoupdate = 5

    def getHeader(self):
        if self.bat != 1: return 'Main Battery'
        return 'Secondary Battery'

    def shouldDisplay(self):
        try:
            return int(f_g_c('/sys/devices/platform/smapi/BAT%s/installed' % self.bat)) == 1
        except:
            return False

    def getListboxRows(self):
        yield Gtk.Label()

        yield TextRow('Manufacturer', '/sys/devices/platform/smapi/BAT%s/manufacturer' % self.bat, True)
        yield TextRow('Model', '/sys/devices/platform/smapi/BAT%s/model' % self.bat)

        yield TextRow('Cycle Count', '/sys/devices/platform/smapi/BAT%s/cycle_count' % self.bat)

        temperatureVal = f_g_c('/sys/devices/platform/smapi/BAT%s/temperature' % self.bat)
        yield TextRow('Temperature', int(temperatureVal)/1000, frmt='%d°C', plain=True)

        yield TextRow('Current state', '/sys/devices/platform/smapi/BAT%s/state' % self.bat, True)
        stateVal = f_g_c('/sys/devices/platform/smapi/BAT%s/state' % self.bat)
        if stateVal == 'charging':
            yield TextRow('Remainging charging time',
                '/sys/devices/platform/smapi/BAT%s/remaining_charging_time' % self.bat,
                frmt='%s minutes'
            )
        elif stateVal == 'idle':
            pass
        else:
            yield TextRow('Remainging running time',
                '/sys/devices/platform/smapi/BAT%s/remaining_running_time_now' % self.bat,
                frmt='%s minutes'
            )

        designCapacityVal = f_g_c('/sys/devices/platform/smapi/BAT%s/design_capacity' % self.bat)
        lastFullCapacityVal = f_g_c('/sys/devices/platform/smapi/BAT%s/last_full_capacity' % self.bat)
        remainingCapacityVal = f_g_c('/sys/devices/platform/smapi/BAT%s/remaining_capacity' % self.bat)
        remainingPercentVal = f_g_c('/sys/devices/platform/smapi/BAT%s/remaining_percent' % self.bat)

        yield PercentageRow('Battery Health',
            float(lastFullCapacityVal)/float(designCapacityVal),
            "%s of %s mWh" % (lastFullCapacityVal, designCapacityVal)
        )

        yield PercentageRow('Remaining Charge',
            float(remainingPercentVal)/100.0,
            "%s of %s mWh" % (remainingCapacityVal, lastFullCapacityVal)
        )

        voltageVal = int(f_g_c('/sys/devices/platform/smapi/BAT%s/voltage' % self.bat))
        yield PercentageRow('Battery Voltage',
            float(voltageVal-10200)/2400.0,
            "%s mV" % voltageVal
        )

        for i in range(4):
            groupVoltageVal = int(f_g_c('/sys/devices/platform/smapi/BAT%s/group%s_voltage' % (self.bat, str(i))))
            if groupVoltageVal > 0:
                yield PercentageRow('Voltage Cell Group %s' % str(i),
                    float(groupVoltageVal-3400)/800.0,
                    "%s mV" % groupVoltageVal
                )
