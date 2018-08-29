import warnings

from time import sleep
import neva.chars as chars

def bcc(packet):
	bcc = 0
	packetstr = packet.decode('ASCII')

	if (packetstr[:1] == chars.SOH.decode('ASCII')) or (packetstr[:1] == chars.STX.decode('ASCII')):
		packetstr = packetstr[1:]

	for c in packetstr:
		bcc ^= ord(c)

	return int(bcc)

def appendbcc(packet):
	packetarr = bytearray(packet)
	packetarr.append(bcc(packet))
	return packetarr

def checkbcc(packet, packetbcc):
	packetbcc = int.from_bytes(packetbcc, 'big')
	newbcc = bcc(packet)
	if (packetbcc != newbcc):
		warnings.warn('Checksum mismatch: {} <> {}'.format(hex(newbcc), hex(packetbcc)), RuntimeWarning)

def hexprint(buffer):
	print(buffer.hex() + ': ' + buffer.decode('ASCII'))

def usleep(usec):
	sleep(usec/1000000.0)

def join_bytes(*args):
	return b''.join(args)

def to_number(str):
	if isinstance(str, (list, tuple)):
		return [to_number(x) for x in str]

	return float(str) if '.' in str else int(float(str))

def kwarg_get(kwargs, key, default = None):
	return kwargs[key] if key in kwargs else default
