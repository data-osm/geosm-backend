__copyright__ = 'Copyright 2021, 3Liz'
__license__ = 'GPL version 3'
__email__ = 'info@3liz.org'


def serverClassFactory(serverIface):
    from .logger import SyslogClient
    return SyslogClient(serverIface)
