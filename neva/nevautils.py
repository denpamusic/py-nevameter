from time import sleep
import warnings

SOH = b'\x01'
STX = b'\x02'
ETX = b'\x03'
EOT = b'\x04'
ACK = b'\x06'
NAK = b'\x15'
CRLF = b'\r\n'

def bcc(packet):
	bcc = 0
	packetstr = packet.decode('ASCII')

	if (packetstr[:1] == SOH.decode('ASCII')) or (packetstr[:1] == STX.decode('ASCII')):
		packetstr = packetstr[1:]

	for c in packetstr:
		bcc ^= ord(c)

	return int(bcc)

def appendbcc(packet):
	packetarr = bytearray(packet)
	packetarr.append(bcc(packet))
	return packetarr

def checkbcc(packet, packetbcc):
	packetbcc = int.from_bytes(packetbcc, byteorder = 'little')
	newbcc = bcc(packet)
	if (packetbcc != newbcc):
		warnings.warn('Checksum mismatch: ' + hex(newbcc) + ' <> ' + hex(packetbcc), RuntimeWarning)

def hexprint(buffer):
	print(buffer.hex()+': '+buffer.decode('ASCII'))

def usleep(usec):
	sleep(usec/1000000.0)

def join_bytes(*args):
	return b''.join(args)

def to_number(str):
	return float(str) if ('.' in str) else int(float(str))
