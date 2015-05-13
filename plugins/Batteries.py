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

    def getRows(self):
        yield Gtk.Label()

        batteryInfo = {}
        data = f_g_c('/sys/class/power_supply/BAT%s/uevent' % self.bat)

        for line in data.split('\n'):
                l=line.split('=')
                batteryInfo[l[0]] = l[1]

        yield TextRow('Manufacturer', batteryInfo['POWER_SUPPLY_MANUFACTURER'], True, plain=True)
        yield TextRow('Model', batteryInfo['POWER_SUPPLY_MODEL_NAME'], plain=True)

        yield TextRow('Cycle Count', '/sys/devices/platform/smapi/BAT%s/cycle_count' % self.bat)

        temperatureVal = f_g_c('/sys/devices/platform/smapi/BAT%s/temperature' % self.bat)
        yield TextRow('Temperature', int(temperatureVal)/1000, frmt='%d°C', plain=True)

        yield TextRow('Current state', batteryInfo['POWER_SUPPLY_STATUS'].replace("Unknown", "Idle"), plain=True)
        stateVal = batteryInfo['POWER_SUPPLY_STATUS']
        if stateVal == 'Charging':
            yield TextRow('Remainging charging time',
                '/sys/devices/platform/smapi/BAT%s/remaining_charging_time' % self.bat,
                frmt='%s minutes'
            )
        elif stateVal == 'Unknown':
            pass
        else:
            yield TextRow('Remainging running time',
                '/sys/devices/platform/smapi/BAT%s/remaining_running_time_now' % self.bat,
                frmt='%s minutes'
            )

        designCapacityVal = int(int(batteryInfo['POWER_SUPPLY_ENERGY_FULL_DESIGN'])/1000)
        lastFullCapacityVal = int(int(batteryInfo['POWER_SUPPLY_ENERGY_FULL'])/1000)
        remainingCapacityVal = int(int(batteryInfo['POWER_SUPPLY_ENERGY_NOW'])/1000)
        remainingPercentVal = batteryInfo['POWER_SUPPLY_CAPACITY']

        yield PercentageRow('Battery Health',
            float(lastFullCapacityVal)/float(designCapacityVal),
            "%s of %s mWh" % (lastFullCapacityVal, designCapacityVal)
        )

        yield PercentageRow('Remaining Charge',
            float(remainingPercentVal)/100.0,
            "%s of %s mWh" % (remainingCapacityVal, lastFullCapacityVal)
        )

        voltageVal = int(int(batteryInfo['POWER_SUPPLY_VOLTAGE_NOW'])/1000)
        yield PercentageRow('Battery Voltage',
            float(voltageVal-(int(batteryInfo['POWER_SUPPLY_VOLTAGE_MIN_DESIGN'])/1000))/1650.0,
            "%s mV" % voltageVal
        )

        for i in range(4):
            groupVoltageVal = int(f_g_c('/sys/devices/platform/smapi/BAT%s/group%s_voltage' % (self.bat, str(i))))
            if groupVoltageVal > 0:
                yield PercentageRow('Voltage Cell Group %s' % str(i),
                    float(groupVoltageVal-3400)/800.0,
                    "%s mV" % groupVoltageVal
                )
