#!/usr/bin/env python3

import neva
from datetime import date, timedelta

def month_profile(month):
	if (month > date.today().month):
		raise RuntimeError("Couldn't fetch power profile from the future")

	dates = []
	power = []

	days = range((date.today() - date(date.today().year, month, 1)).days + 1)

	with neva.connect(address) as n:
		start = int(n.addr('power_profile_start'), 16)
		for day in days:
			current_date = date.today() - timedelta(days=day)
			if (current_date.month != month):
				continue

			dates.append(current_date.strftime('%Y-%m-%d'))
			power.append(n.readaddr(bytes(format(start + day, 'X'), 'ASCII')))

	return [list(reversed(dates)), list(reversed(power))]

# get power profile for July
dates, readings = month_profile(7)
