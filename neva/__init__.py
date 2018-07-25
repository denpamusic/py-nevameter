from .nevameter import NevaMeter

def connect(url, **kwargs):
	nevameter = NevaMeter(url, **kwargs)
	nevameter.connect()
	return nevameter

def read(url, **args, **kwargs):
	with connect(url, **kwargs) as n:
		return [n.readaddr(x.upper()) for x in args]
