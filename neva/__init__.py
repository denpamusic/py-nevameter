from .nevameter import NevaMeter

def connect(url, **kwargs):
	nevameter = NevaMeter(url, **kwargs)
	nevameter.connect()
	return nevameter
