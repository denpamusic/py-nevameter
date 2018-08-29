from time import sleep
import neva.ascii as ascii

def dump(data):
    ''' Dumps string or hex representation of data '''
    print(data if isinstance(data, str) else data.hex() + ': ' + ascii.btoa(data))

def usleep(usec):
    sleep(usec / 1000000.0)

def join_bytes(*args):
    return b''.join(args)

def to_number(str):
    ''' Converts string or list|tuple of strings to number '''
    if isinstance(str, (list, tuple)):
        return [to_number(x) for x in str]

    return float(str) if '.' in str else int(float(str))

def kwarg_get(kwargs, key, default = None):
    ''' Gets kwarg by name '''
    return kwargs[key] if key in kwargs else default
