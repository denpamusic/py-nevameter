import re
import warnings

from . import bcc, util, ascii, verbose

class Connection:
    char_pattern = r'\[([A-Z]{2,3})\]'
    _sequence = 0

    def __init__(self, serial, debug = False):
        self._serial = serial
        self._debug = debug

    def _parse(self, payload):
        ''' Parses payload and replaces control characters '''
        append_bcc = False

        chars = re.findall(self.char_pattern, payload)
        for char in chars:
            if char == 'BCC':
                append_bcc = True
                payload = payload.replace('[%s]' % char, '')

            if hasattr(ascii, char):
                byte = getattr(ascii, char)
                payload = payload.replace('[%s]' % char, ascii.btoa(byte))

        payload = ascii.atob(payload)
        return bcc.append(payload) if append_bcc else payload

    def setBaudrate(self, baudrate):
        ''' Sets serial connection baudrate '''
        util.usleep(300000)
        self._serial.baudrate = baudrate

    def write(self, payload):
        ''' Writes payload to serial connection '''
        payload = self._parse(payload)

        if self._debug:
            self._sequence += 1
            verbose.sent(payload, self._sequence)

        self._serial.write(payload)

    def read(self, until = ascii.ETX, check_bcc = True):
        ''' Reads data from serial connection '''
        if until == ascii.ACK:
            return self._serial.read(1) == until

        response = self._serial.read_until(until)
        if self._debug:
            self._sequence += 1
            verbose.received(response, self._sequence)

        if check_bcc and not bcc.valid(response, self._serial.read(1)):
            warnings.warn('Block checksum mismatch.', RuntimeWarning)

        return response

    def close(self):
        ''' Closes serial connection '''
        if self._serial.isOpen():
            self.write('[SOH]B0[ETX][BCC]')
            util.usleep(50000)
            self._serial.flush()
            self._serial.close()
