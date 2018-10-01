import importlib
from . import ascii
from time import sleep

def split_str(str, length = 2):
    ''' Splits string into pieces of certain length '''
    return [str[i:i+length] for i in range(0, len(str), length)]

def hexify(data):
    ''' Dumps string or hex representation of data '''
    return ' '.join(split_str(data.hex())) + ': ' + ascii.btoa(data)

def usleep(usec):
    ''' Sleeps for microseconds '''
    sleep(usec / 1000000.0)

def to_number(str):
    ''' Converts string or list|tuple of strings to number '''
    if isinstance(str, (list, tuple)):
        return [to_number(x) for x in str]

    return float(str) if '.' in str else int(float(str))

def load_module(module):
    ''' Loads module by path '''
    parts = module.split('.')
    for length in range(1, len(parts)):
        importlib.import_module('.'.join(parts[:length]))

    return importlib.import_module(module)
