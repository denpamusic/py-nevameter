import re
import serial
import logging
import warnings

from . import util, ascii
from neva.connection import Connection

class Meter:
    def __init__(self, url, **kwargs):
        ''' Creates meter instance and initializes connection '''
        _serial = serial.serial_for_url(
            url,
            timeout  = kwargs.get('timeout', 600),
            baudrate = kwargs.get('baudrate', 300),
            parity   = kwargs.get('parity', serial.PARITY_EVEN),
            bytesize = kwargs.get('bytesize', serial.SEVENBITS),
            stopbits = kwargs.get('stopbits', serial.STOPBITS_ONE),
            **kwargs
        )
        self.connection = Connection(_serial)
        self._logger = logging.getLogger(__name__)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.close()

    def _parse_range(self, addresses):
        ''' Parses list to address range '''
        limits = [int(x, 16) for x in addresses]
        limits = range(min(limits), max(limits) + 1)
        return [ascii.atob(format(x, 'X')) for x in limits]

    def _parse_version(self, response):
        ''' Parses version string '''
        m = re.search(r'\/(...)(\d)(....)(.*)\.(.*)', ascii.btoa(response))
        self.vendor, self.speed, self.model, self.model_number, self.version = m.group(1, 2, 3, 4, 5)

    def _sanitize(self, response):
        return response.split(',') if ',' in response else response

    def _load_addresses(self):
        ''' Loads addresses for specified model number '''
        try:
            module = '%s-%s-%s' % (self.vendor, self.model, self.model_number)
            self._addresses = util.load_module('neva.meters.' + module.lower())
            self._logger.info('Loaded addresses from [%s.py]', module.lower())
        except ImportError:
            warnings.warn('Unknown meter [%s]' % module, RuntimeWarning)

    def resolve(self, name):
        ''' Resolves address alias to byte representation '''
        if not isinstance(name, str):
            return ascii.btoa(name)

        key = name.lower()
        if not hasattr(self._addresses, key):
            raise LookupError('Address not found [%s]' % name)

        return getattr(self._addresses, key)

    def connect(self):
        ''' Initializes connection to the meter '''
        connection = self.connection
        connection.write('/?![CR][LF]')
        self._parse_version(connection.read(until = ascii.LF, check_bcc = False))
        self._load_addresses()
        connection.negotiateSpeed(self.speed)
        connection.write('[SOH]P1[STX](00000000)[ETX][BCC]')
        if not connection.read(until = ascii.ACK):
            raise RuntimeError('Invalid password')

    def read(self, name, *args, **kwargs):
        '''\
            Reads data from address by byte representation
            or by address alias.
        '''
        address = self.resolve(name)
        if isinstance(address, (list, tuple)):
            return self.read_range(address, len(address))

        args = ','.join(args)
        self.connection.write('[SOH]R1[STX]%s(%s)[ETX][BCC]' % (address, args))
        response = self.connection.read()
        m = re.search(re.escape(address) + r'\((.*)\)', ascii.btoa(response))
        if m is None:
            warnings.warn('Command not supported [%s]' % address, RuntimeWarning)
            return

        result = self._sanitize(m.group(1))
        raw = kwargs.get('raw', ['date', 'time'])
        return result if isinstance(name, str) and (name in raw) else util.to_number(result)

    def read_range(self, name, length, offset = 0):
        ''' Reads range af addresses '''
        addresses = self.resolve(name) if isinstance(name, str) else name
        return [self.read(x) for x in self._parse_range(addresses)[offset:][:length]]

    def close(self):
        ''' Closes serial connection '''
        self.connection.close()
