import serial
import re
import warnings
import importlib
from .nevautils import *

class NevaMeter:
	__ADDRESSES__ = None
	__SERIAL__ = None
	__DEBUG__ = False
	__SPEEDS__ = (300, 600, 1200, 2400, 4800, 9600)
	__OPEN__ = False

	model = None
	model_number = None
	version = None
	manufacturer = None

	__SKIP_SANITIZE__ = ('TIME', 'DATE')

	def __init__(self, url, debug = False):
		self.__SERIAL__ = serial.serial_for_url(
			url,
			timeout=600,
			baudrate=self.__SPEEDS__[0],
			parity = serial.PARITY_EVEN,
			bytesize = serial.SEVENBITS,
			stopbits = serial.STOPBITS_ONE
		)
		self.__OPEN__ = True
		self.__DEBUG__ = debug

    def __enter__(self):
        return self

	def __exit__(self, exc_type, exc_value, traceback):
		self.close()

	def __set_speed__(self, speed):
		if self.__DEBUG__:
			print('Setting baudrate to {0} bps...'.format(self.__SPEEDS__[int(speed)]))
		self.__SERIAL__.write(join_bytes(ACK, b'0', bytes(speed, 'ASCII'), b'1', CRLF))
		usleep(300000)
		self.__SERIAL__.baudrate = self.__SPEEDS__[int(speed)]

	def __import_addresses__(self):
		try:
			importlib.import_module('.meters', 'neva')
			self.__ADDRESSES__ = importlib.import_module('.meters.{0}'.format(self.model_number), 'neva')
		except ImportError:
			warnings.warn(
				'No addresses found for {} {}'.format(self.model, self.model_number),
				RuntimeWarning
			)
			pass

	def __parse_version_str__(self, versionstr):
		m = re.search(r'(....)((?:MT)?(?:.*))\.(.*)', versionstr)
		self.model, self.model_number, self.version = m.group(1, 2, 3)

	def __sanitize_response__(self, response):
		return [to_number(x) for x in response.split(',')] if (',' in response) else to_number(response)

	def connect(self):
		self.__SERIAL__.write(join_bytes(b'/?!', CRLF))
		response = self.__SERIAL__.read_until()
		m = re.search(r'/(...)(\d)(.*)', response.decode('ASCII'))
		self.manufacturer, speed, version = m.group(1, 2, 3)
		self.__parse_version_str__(version)
		self.__import_addresses__()
		if self.__DEBUG__:
			print('Connecting to {} {} {} v{}...'.format(self.manufacturer, self.model, self.model_number, self.version))

		self.__set_speed__(speed)
		response=self.__SERIAL__.read_until(ETX)
		checkbcc(response, self.__SERIAL__.read(1))
		if self.__DEBUG__:
			hexprint(response)

		self.auth()

	def auth(self):
		tries = 0

		while True:
			self.__SERIAL__.write(self.password('00000000'))
			response = self.__SERIAL__.read(1)
			if self.__DEBUG__:
				hexprint(response)

			if (response == ACK):
				break

			if (tries >= 3):
				raise RuntimeError('Too many authentication attempts')
			usleep(500000 + 100000 * tries)
			tries += 1

	def password(self, pwd):
		return appendbcc(join_bytes(SOH, b'P1', STX, b'(', bytes(pwd, 'ASCII'), b')', ETX))

	def addr(self, name):
		if hasattr(self.__ADDRESSES__, name):
			return getattr(self.__ADDRESSES__, name)
		else:
			raise RuntimeError('No address named "{}" found'.format(name))

	def readaddr(self, address, args = ''):
		if isinstance(address, str):
			address = self.addr(address)

		command = appendbcc(join_bytes(SOH, b'R1', STX, address, b'(', bytes(args, 'ASCII') , b')', ETX))
		if self.__DEBUG__:
			print('Send:')
			hexprint(command)

		self.__SERIAL__.write(command)
		response = self.__SERIAL__.read_until(ETX)

		if self.__DEBUG__:
			print('Receive:')
			hexprint(response)

		checkbcc(response, self.__SERIAL__.read(1))
		m = re.search(address.decode('ASCII') + r'\((.*)\)', response.decode('ASCII'))

		if m is None:
			warnings.warn('Command not supported', RuntimeWarning)
			return ''

		for a in self.__SKIP_SANITIZE__:
			if (self.addr(a) == address):
				return m.group(1)

		return self.__sanitize_response__(m.group(1))

	def close(self):
		if self.__OPEN__:
			self.__SERIAL__.write(appendbcc(join_bytes(SOH, b'B0', ETX)))
			usleep(500000)
			self.__SERIAL__.flush()
			self.__SERIAL__.close()
			self.__OPEN__ = False
