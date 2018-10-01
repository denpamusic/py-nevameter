import warnings
from . import ascii

def bcc(packet):
    ''' Calculates Block Check Character '''
    bcc = 0
    packetstr = ascii.btoa(packet)
    if packetstr[:1] in [ascii.btoa(ascii.SOH), ascii.btoa(ascii.STX)]:
        packetstr = packetstr[1:]

    for c in packetstr:
        bcc ^= ord(c)

    return int(bcc)

def append(packet):
    ''' Appends Block Check Character to the packet '''
    packetarr = bytearray(packet)
    packetarr.append(bcc(packet))
    return packetarr

def valid(packet, packetbcc):
    ''' Checks Block Check Character of the packet '''
    packetbcc = int.from_bytes(packetbcc, 'big')
    newbcc = bcc(packet)
    return packetbcc == newbcc
