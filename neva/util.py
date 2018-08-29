import warnings
from time import sleep
import neva.ascii as ascii

def bcc(packet):
    ''' Calculates Block Check Character '''
    bcc = 0
    packetstr = ascii.btoa(packet)
    if packetstr[:1] in [ascii.btoa(ascii.SOH), ascii.btoa(ascii.STX)]:
        packetstr = packetstr[1:]

    for c in packetstr:
        bcc ^= ord(c)

    return int(bcc)

def appendbcc(packet):
    ''' Appends Block Check Character to the packet '''
    packetarr = bytearray(packet)
    packetarr.append(bcc(packet))
    return packetarr

def checkbcc(packet, packetbcc):
    ''' Checks Block Check Character of the packet '''
    packetbcc = int.from_bytes(packetbcc, 'big')
    newbcc = bcc(packet)
    if (packetbcc != newbcc):
        warnings.warn(
            'Checksum mismatch: {} <> {}'.format(hex(newbcc), hex(packetbcc)),
            RuntimeWarning
        )

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
