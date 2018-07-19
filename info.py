#!/usr/bin/python3

import neva
import neva.meters
from datetime import datetime

n = neva.connect('rfc2217://172.30.1.123:5000', debug = False)

date = n.readaddr('DATE')
time = n.readaddr('TIME')
datetime = datetime.strptime(date+time, '%y%m%d%H%M%S')
readings = n.readaddr('READINGS')
total, t1, t2, t3, t4 = readings.split(',')

print('======= PARAMETERS =======')
print('Date: {0}'.format(datetime.strftime('%d.%m.%Y')))
print('Time: {0}'.format(datetime.strftime('%H:%M:%S')))
print('Voltage: {0} V'.format(n.readaddr('VOLTAGE')))
print('Current: {0} A'.format(n.readaddr('CURRENT')))
print('Active Power: {0} kW'.format(n.readaddr('ACTIVE_POWER')))
print('Power Factor: {0}'.format(n.readaddr('POWER_FACTOR')))
print('Temperature: {0} C'.format(n.readaddr('TEMPERATURE')))
print('Frequency: {0} Hz'.format(n.readaddr('FREQUENCY')))
print('======== READINGS ========')
print('Day   : {0} KWh'.format(t1))
print('Night : {0} KWh'.format(t2))
print('Total : {0} KWh'.format(total))

n.close()
