import re
import serial
import warnings
import importlib
import neva.bcc as bcc
import neva.util as util
import neva.ascii as ascii

class Meter:
    SPEEDS = (300, 600, 1200, 2400, 4800, 9600)

    def __init__(self, url, **kwargs):
        ''' Creates serial connection '''
        self._serial = serial.serial_for_url(
            url,
            timeout  = util.kwarg_get(kwargs, 'timeout', 600),
            baudrate = util.kwarg_get(kwargs, 'baudrate', self.SPEEDS[0]),
            parity   = util.kwarg_get(kwargs, 'parity',   serial.PARITY_EVEN),
            bytesize = util.kwarg_get(kwargs, 'bytesize', serial.SEVENBITS),
            stopbits = util.kwarg_get(kwargs, 'stopbits', serial.STOPBITS_ONE)
        )
        self._debug = util.kwarg_get(kwargs, 'debug', False)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def _import_addresses(self, model_number):
        ''' Imports addresses aliases for specified model number '''
        try:
            importlib.import_module('.meters', 'neva')
            self._addresses = importlib.import_module('.meters.{}'.format(model_number), 'neva')
        except ImportError:
            warnings.warn(
                'No addresses found for {}'.format(model_number),
                RuntimeWarning
            )
            pass

    def _parse_version(self, versionstr):
        ''' Parses meter version string '''
        m = re.search(r'(....)((?:MT)?(?:.*))\.(.*)', versionstr)
        return m.group(1, 2, 3)

    def _sanitize(self, response):
        return response.split(',') if ',' in response else response

    def _debug_message(self, message):
        ''' Prints message if debug mode is enabled '''
        if self._debug:
            util.dump(message)

    def connect(self):
        ''' Initializes connection to the meter '''
        self.write(util.join_bytes(b'/?!', ascii.CRLF))
        response = self.read_until()
        m = re.search(r'/(...)(\d)(.*)', ascii.btoa(response))
        self.manufacturer, speed, version_str = m.group(1, 2, 3)
        self.model, self.model_number, self.version = self._parse_version(version_str)
        self._import_addresses(self.model_number)
        self._debug_message('Connecting to {} {} {} v{}...'.format(self.manufacturer, self.model, self.model_number, self.version))
        self.set_speed(speed)
        response = self.read_until(ascii.ETX, check_bcc = True)
        self._debug_message(response)
        self.auth()

    def set_speed(self, speed):
        ''' Sets serial baudrate and transmits it to meter '''
        self._debug_message('Setting baudrate to {} bps...'.format(self.SPEEDS[int(speed)]))
        self.write(util.join_bytes(ascii.ACK, b'0', ascii.atob(speed), b'1', ascii.CRLF))
        util.usleep(300000)
        self._serial.baudrate = self.SPEEDS[int(speed)]

    def auth(self):
        ''' Performs authentication with default password '''
        tries = 0
        while True:
            self.write(self.password('00000000'))
            response = self.read(1)
            self._debug_message(response)
            if (response == ascii.ACK):
                break

            if (tries >= 3):
                raise RuntimeError('Too many authentication attempts')

            util.usleep(500000 + 100000 * tries)
            tries += 1

    def password(self, pwd):
        ''' Constructs authentication packet '''
        return bcc.append(util.join_bytes(
            ascii.SOH, b'P1', ascii.STX,
            b'(', ascii.atob(pwd), b')', ascii.ETX
        ))

    def command(self, address, *args):
        ''' Constructs command packet '''
        return bcc.append(util.join_bytes(
            ascii.SOH, b'R1', ascii.STX, address,
            b'(', ascii.atob(','.join(args)) , b')', ascii.ETX
        ))

    def resolve(self, name):
        ''' Resolves address alias to byte representation '''
        key = name.upper()
        if not hasattr(self._addresses, key):
            raise RuntimeError('No address named "{}" found'.format(name))

        return getattr(self._addresses, key)

    def readaddr(self, name, *args, **kwargs):
        ''' Reads data from meter address by byte representation
        or by address alias '''
        address = self.resolve(name) if isinstance(name, str) else name
        command = self.command(address, *args)
        self.write(command)
        response = self.read_until(ascii.ETX, check_bcc = True)
        self._debug_message(command)
        self._debug_message(response)
        m = re.search(ascii.btoa(address) + r'\((.*)\)', ascii.btoa(response))
        if m is None:
            warnings.warn('Command not supported', RuntimeWarning)
            return ''

        result = self._sanitize(m.group(1))
        raw = util.kwarg_get(kwargs, 'raw', ['date', 'time'])
        return result if isinstance(name, str) and (name in raw) else util.to_number(result)

    def write(self, bytes):
        ''' Writes bytes to serial port '''
        if not self._serial.isOpen():
            raise RuntimeError('Could not write. Serial is not open.')

        return self._serial.write(bytes)

    def read(self, length):
        ''' Reads bytes from serial port '''
        if not self._serial.isOpen():
            raise RuntimeError('Could not read. Serial is not open.')

        return self._serial.read(length)

    def read_until(self, expect = ascii.LF, **kwargs):
        ''' Reads from serial port until character '''
        if not self._serial.isOpen():
            raise RuntimeError('Could not read. Serial is not open.')

        response = self._serial.read_until(expect)
        if util.kwarg_get(kwargs, 'check_bcc', False):
            bcc.check(response, self._serial.read(1))

        return response

    def close(self):
        ''' Closes serial connection '''
        if self._serial.isOpen():
            self._serial.write(
                bcc.append(util.join_bytes(ascii.SOH, b'B0', ascii.ETX))
            )
            util.usleep(500000)
            self._serial.flush()
            self._serial.close()
