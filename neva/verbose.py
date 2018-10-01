from . import util

from datetime import datetime

def _output(template, sequence, data):
    ''' Prints data in stdout '''
    now = datetime.now()
    data = util.hexify(data)
    print(template % (sequence, now, data))

def sent(data, sequence):
    ''' Prints data with sent template '''
    _output('%d >> %s  %s', sequence, data)

def received(data, sequence):
    ''' Prints data with received template '''
    _output('%d << %s  %s', sequence, data)
