#!/usr/bin/python3

import neva
import neva.meters
from datetime import datetime

n = neva.connect('rfc2217://172.30.1.123:5000', debug = False)

date = n.readaddr(neva.meters.MT113.DATE)
time = n.readaddr(neva.meters.MT113.TIME)
datetime = datetime.strptime(date+time, '%y%m%d%H%M%S')
readings = n.readaddr(neva.meters.MT113.READINGS)
total, t1, t2, t3, t4 = readings.split(',')
print('======= PARAMETERS =======')
print('Date: {0}'.format(datetime))
print('Voltage: {0} V'.format(n.readaddr(neva.meters.MT113.VOLTAGE)))
print('Current: {0} A'.format(n.readaddr(neva.meters.MT113.CURRENT)))
print('Active Power: {0} kW'.format(n.readaddr(neva.meters.MT113.ACTIVE_POWER)))
print('Power Factor: {0}'.format(n.readaddr(neva.meters.MT113.POWER_FACTOR)))
print('Temperature: {0} C'.format(n.readaddr(neva.meters.MT113.TEMPERATURE)))
print('Frequency: {0} Hz'.format(n.readaddr(neva.meters.MT113.FREQUENCY)))
print('======== READINGS ========')
print('Day   : {0} KWh'.format(t1))
print('Night : {0} KWh'.format(t2))
print('Total : {0} KWh'.format(total))

n.close()
