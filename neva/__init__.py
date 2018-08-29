from neva.meter import Meter

def connect(url, **kwargs):
	meter = Meter(url, **kwargs)
	meter.connect()
	return meter

def read(url, *args, **kwargs):
	with connect(url, **kwargs) as n:
		return [n.readaddr(x, **kwargs) for x in args]
