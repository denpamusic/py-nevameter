import re
import warnings
import logging

from . import bcc, util, ascii

class Connection:
    char_pattern = r'\[([A-Z]{2,3})\]'

    _speeds = (300, 600, 1200, 2400, 4800, 9600)
    _sequence = 0

    def __init__(self, serial):
        self._serial = serial
        self._logger = logging.getLogger(__name__)

    def _parse(self, payload):
        ''' Parses payload and replaces control characters '''
        append_bcc = False

        chars = re.findall(self.char_pattern, payload)
        for char in chars:
            if char == 'BCC':
                append_bcc = True
                payload = payload.replace('[BCC]', '')
            elif hasattr(ascii, char):
                byte = getattr(ascii, char)
                payload = payload.replace('[%s]' % char, ascii.btoa(byte))
            else:
                warnings.warn('Unknown character [%s]' % char, RuntimeWarning)

        payload = ascii.atob(payload)
        return bcc.append(payload) if append_bcc else payload

    def negotiateSpeed(self, speed):
        ''' Sets serial connection baudrate '''
        baudrate = self._speeds[int(speed)];
        self._logger.info('Negotiating baudrate to %s bps...', baudrate)
        self.write('[ACK]0%s1[CR][LF]' % speed)
        util.usleep(300000)
        self._serial.baudrate = baudrate
        self.read()

    def write(self, payload):
        ''' Writes payload to serial connection '''
        self._sequence += 1
        payload = self._parse(payload)
        self._logger.debug('%s >> %s', self._sequence, util.hexify(payload))
        self._serial.write(payload)

    def read(self, until = ascii.ETX, check_bcc = True):
        ''' Reads data from serial connection '''
        self._sequence += 1
        if until == ascii.ACK:
            return self._serial.read(1) == until

        response = self._serial.read_until(until)
        self._logger.debug('%s << %s', self._sequence, util.hexify(response))
        if check_bcc and not bcc.valid(response, self._serial.read(1)):
            self._logger.warning('Checksum mismatch [%s]', ascii.btoa(response))

        return response

    def close(self):
        ''' Closes serial connection '''
        if self._serial.isOpen():
            self.write('[SOH]B0[ETX][BCC]')
            util.usleep(50000)
            self._serial.flush()
            self._serial.close()
