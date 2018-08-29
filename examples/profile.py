#!/usr/bin/env python3

import neva
from datetime import date, timedelta

def profile_for_days(url, days, offset = 0):
    ''' Gets power profile for number of days
    starting from offset days ago '''
    dates = []
    power = []

    with neva.connect(url) as n:
        start = int(n.resolve('power_profile_start'), 16) + offset
        for day in range(days):
            current_date = date.today() - timedelta(days = day + offset)
            dates.append(current_date.strftime('%Y-%m-%d'))
            power.append(n.readaddr(bytes(format(start + day, 'X'), 'ASCII')))

        return [list(reversed(dates)), list(reversed(power))]

def profile_for_month(url, month):
    ''' Gets power profile for month by month number.
    Missing data is padded with zeros '''
    if (month > date.today().month):
        raise RuntimeError("Couldn't fetch power profile from the future")

    days = (date(date.today().year, month + 1, 1) - date(date.today().year, month, 1)).days
    offset = (date.today() - date(date.today().year, month, days)).days
    if (offset <= 0):
            days = (date.today() - date(date.today().year, month, 1)).days + 1

    dates, power = profile_for_days(url, days, (offset if (offset > 0) else 0))
    dates = __pad_month__(dates, offset)
    return [dates, pad(power, len(dates), list_of(0.0, 24))]

# get power profile for July
dates, readings = profile_for_month('rfc2217://172.30.1.123:5000', 7)

# get power profile for last 3 days
dates, readings = profile_for_days('rfc2217://172.30.1.123:5000', 3)

# get power profile for last 3 days excluding today
dates, readings = profile_for_days('rfc2217://172.30.1.123:5000', 3, 1)
