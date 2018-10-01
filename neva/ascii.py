SOH = b'\x01'
STX = b'\x02'
ETX = b'\x03'
EOT = b'\x04'
ACK = b'\x06'
NAK = b'\x15'
LF = b'\n'
CR = b'\r'

def atob(ascii):
    ''' Converts ascii to bytes '''
    return bytes(ascii, 'ASCII')

def btoa(bytes):
    ''' Converts bytes to ascii '''
    return bytes.decode('ASCII')
