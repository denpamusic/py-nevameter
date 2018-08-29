import re
import serial
import warnings
import importlib
import neva.util as util

class Meter:
	__ADDRESSES__ = None
	__SERIAL__ = None
	__DEBUG__ = False
	__SPEEDS__ = (300, 600, 1200, 2400, 4800, 9600)
	__OPEN__ = False

	model = None
	model_number = None
	version = None
	manufacturer = None

	def __init__(self, url, **kwargs):
		self.__SERIAL__ = serial.serial_for_url(
			url,
			timeout  = util.kwarg_get(kwargs, 'timeout', 600),
			baudrate = self.__SPEEDS__[0],
			parity   = util.kwarg_get(kwargs, 'parity',   serial.PARITY_EVEN),
			bytesize = util.kwarg_get(kwargs, 'bytesize', serial.SEVENBITS),
			stopbits = util.kwarg_get(kwargs, 'stopbits', serial.STOPBITS_ONE)
		)
		self.__OPEN__  = True
		self.__DEBUG__ = util.kwarg_get(kwargs, 'debug', False)

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self.close()

	def __set_speed__(self, speed):
		if self.__DEBUG__:
			print('Setting baudrate to {} bps...'.format(self.__SPEEDS__[int(speed)]))
		self.write(util.join_bytes(ACK, b'0', bytes(speed, 'ASCII'), b'1', CRLF))
		util.usleep(300000)
		self.__SERIAL__.baudrate = self.__SPEEDS__[int(speed)]

	def __import_addresses__(self):
		try:
			importlib.import_module('.meters', 'neva')
			self.__ADDRESSES__ = importlib.import_module('.meters.{}'.format(self.model_number), 'neva')
		except ImportError:
			warnings.warn(
				'No addresses found for {} {}'.format(self.model, self.model_number),
				RuntimeWarning
			)
			pass

	def __parse_version_str__(self, versionstr):
		m = re.search(r'(....)((?:MT)?(?:.*))\.(.*)', versionstr)
		self.model, self.model_number, self.version = m.group(1, 2, 3)

	def __sanitize__(self, response):
		return response.split(',') if ',' in response else response

	def connect(self):
		self.write(util.join_bytes(b'/?!', CRLF))
		response = self.read_until()
		m = re.search(r'/(...)(\d)(.*)', response.decode('ASCII'))
		self.manufacturer, speed, version = m.group(1, 2, 3)
		self.__parse_version_str__(version)
		self.__import_addresses__()
		if self.__DEBUG__:
			print('Connecting to {} {} {} v{}...'.format(self.manufacturer, self.model, self.model_number, self.version))

		self.__set_speed__(speed)
		response=self.read_until(ETX)
		util.checkbcc(response, self.read(1))
		if self.__DEBUG__:
			util.hexprint(response)

		self.auth()

	def auth(self):
		tries = 0

		while True:
			self.write(self.password('00000000'))
			response = self.read(1)
			if self.__DEBUG__:
				util.hexprint(response)

			if (response == ACK):
				break

			if (tries >= 3):
				raise RuntimeError('Too many authentication attempts')
			util.usleep(500000 + 100000 * tries)
			tries += 1

	def password(self, pwd):
		return util.appendbcc(util.join_bytes(SOH, b'P1', STX, b'(', bytes(pwd, 'ASCII'), b')', ETX))

	def resolve(self, name):
		key = name.upper()
		if not hasattr(self.__ADDRESSES__, key):
			raise RuntimeError('No address named "{}" found'.format(name))

		return getattr(self.__ADDRESSES__, key)

	def readaddr(self, name, *args, **kwargs):
		address = self.resolve(name) if isinstance(name, str) else name
		command = util.appendbcc(util.join_bytes(SOH, b'R1', STX, address, b'(', bytes(','.join(args), 'ASCII') , b')', ETX))
		if self.__DEBUG__:
			print('Send:')
			util.hexprint(command)

		self.write(command)
		response = self.read_until(ETX)
		if self.__DEBUG__:
			print('Receive:')
			util.hexprint(response)

		util.checkbcc(response, self.read(1))
		m = re.search(address.decode('ASCII') + r'\((.*)\)', response.decode('ASCII'))
		if m is None:
			warnings.warn('Command not supported', RuntimeWarning)
			return ''

		result = self.__sanitize__(m.group(1))
		raw = util.kwarg_get(kwargs, 'raw', ['date', 'time'])
		return result if isinstance(name, str) and (name in raw) else util.to_number(result)

	def write(self, bytes):
		if not self.__OPEN__:
			raise RuntimeError('Could not write. Connection is not open.')

		return self.__SERIAL__.write(bytes)

	def read_until(self, expect = LF):
		if not self.__OPEN__:
			raise RuntimeError('Could not read. Connection is not open.')

		return self.__SERIAL__.read_until(expect)

	def read(self, length):
		if not self.__OPEN__:
			raise RuntimeError('Could not read. Connection is not open.')

		return self.__SERIAL__.read(length)

	def close(self):
		if self.__OPEN__:
			self.__SERIAL__.write(util.appendbcc(util.join_bytes(SOH, b'B0', ETX)))
			util.usleep(500000)
			self.__SERIAL__.flush()
			self.__SERIAL__.close()
			self.__OPEN__ = False
