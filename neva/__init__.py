from neva.meter import Meter

def connect(url, **kwargs):
    ''' Creates instance and connects to meter '''
    meter = Meter(url, **kwargs)
    meter.connect()
    return meter

def read(url, *args, **kwargs):
    ''' Reads data from list of addresses or address aliases '''
    with connect(url, **kwargs) as n:
        return [n.readaddr(x, **kwargs) for x in args]
