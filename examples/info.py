#!/usr/bin/env python3

import neva

keys = (
	'date',
	'time',
	'voltage',
	'current',
	'active_power',
	'power_factor',
	'temperature',
	'frequency',
	'readings'
)

values = neva.read('rfc2217://172.30.1.123:5000', *keys)
data = dict(zip(keys, values))
data['total'], data['t1'], data['t2'], data['t3'], data['t4'] = data['readings']

print("""\
======== PARAMETERS ========
Date         : {date}
Time         : {time}
Voltage      : {voltage}
Current      : {current}
Active Power : {active_power}
Power Factor : {power_factor}
Temperature  : {temperature}
Frequency    : {frequency}
========= READINGS =========
Day          : {t1}
Night        : {t2}
Total        : {total}
""".format(**data))
