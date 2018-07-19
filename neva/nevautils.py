from time import sleep

SOH = b'\x01'
STX = b'\x02'
ETX = b'\x03'
ACK = b'\x06'
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
	packetbcc = int.from_bytes(packetbcc, byteorder='little')
	newbcc = bcc(packet)
	if (packetbcc != newbcc):
		print('Warning: checksum mismatch: ' + hex(newbcc) + ' <> ' + hex(packetbcc))

def hexprint(buffer):
	print(buffer.hex()+': '+buffer.decode('ASCII'))

def usleep(usec):
	sleep(usec/1000000.0)

def join_bytes(*args):
	return b''.join(args)
