# -*- coding: utf-8 -*-
"""Simple interface to kwallet through dbus.

Allows setting and getting items from any wallet in the Map section.
"""


import binascii
import contextlib
import dbus
import scipy

__version__ = '0.2'


class KWallet(object):
    """Class to handle communication with kwallet through dbus."""

    def __init__(self, application, wallet=None):
        """Initializer.

        Connects through dbus to kwallet.

        @param application application identifier
        @param wallet wallet name
        """
        self.appid = application
        try:
            self.__bus = dbus.SessionBus()
        except dbus.DBusException:
            raise ConnectionRefusedError
        name = u'org.kde.kwalletd'
        object_path = u'/modules/kwalletd'
        self.__kw = self.__bus.get_object(name, object_path)
        interface = u'org.kde.KWallet'
        self.iface = dbus.Interface(self.__kw, dbus_interface=interface)
        if wallet:
            self.wallet = wallet
        else:
            self.wallet = self.iface.localWallet()
        self.__handle = None
        self.__folder = None
        self.__encoding = 'utf-16-be'

    def get(self, entry, key=u'password'):
        """Return the value for the request.

        Raises EntryNotFoundError, if it does not exist.
        """
        res = self._get_dict(entry)
        return res[key]

    @contextlib.contextmanager
    def open(self):
        """Open a connection to a wallet in a context manager instance."""
        self._open()
        yield
        self._close()

    def set_folder(self, folder):
        """Set the desired folder for subsequent operations."""
        if not self.iface.hasFolder(self.__handle, folder, self.appid):
            self.iface.createFolder(self.__handle, folder, self.appid)
        self.__folder = folder

    def set(self, entry, value, key=u'password'):
        """Sets the requested value forthe specified key in the entry."""
        try:
            info = self._get_dict(entry)
        except EntryNotFoundError:
            info = {}
        info[key] = value
        info = self._encode(info)
        info = dbus.ByteArray(info)
        self.iface.writeMap(self.__handle, self.__folder,
                            entry, info, self.appid)

    def _binary_to_int(self, value, base=16):
        """Converts binary data to an integer."""
        return int(binascii.b2a_hex(value), base)

    def _calculate_length(self, data):
        """Calculates the length of the next entry in a dbus.ByteArray."""
        return scipy.int32(len(data)).newbyteorder('B').tostring()

    def _close(self):
        """Close the wallet."""
        self.iface.close(self.__handle, False, self.appid)

    def _decode(self, value):
        """Decode a dbus.ByteArray based on a qmap.

        The first 4 bytes are the number of entries."""
        info = {}
        value = value[4:]
        for (entry, data) in self._next_data(value):
            info[entry] = data
        return info

    def _encode(self, value):
        """Encode a dict to a dbus.ByteArray."""
        data = []
        for (entry, val) in value.items():
            data.append(entry.encode(self.__encoding))
            data.append(val.encode(self.__encoding))
        enc = self._calculate_length(value.keys())
        for d in data:
            enc += self._calculate_length(d) + d
        return enc

    def _get_dict(self, entry):
        """Return the whole dictionary for the specified entry."""
        res = self.iface.readMap(self.__handle, self.__folder,
                                 entry, self.appid,
                                 byte_arrays=True, utf8_strings=True)
        if res == 'None':
            raise EntryNotFoundError(u'Entry %s not found' % entry)
        res = self._decode(res)
        return res

    def _next_data(self, value):
        """Returns a tuple (entry, data) for the next entry.

        Generator function.
        """
        while value:
            (entry, length) = self._next_entry(value)
            value = value[length:]
            (data, length) = self._next_entry(value)
            value = value[length:]
            yield (entry, data)

    def _next_entry(self, value):
        """Returns the next entry of a dbus.ByteArray."""
        length = self._binary_to_int(value[:4])
        data = value[4:length + 4]
        data = data.decode(self.__encoding)
        return (data, length + 4)

    def _open(self):
        """Open the wallet."""
        self.__handle = self.iface.open(self.wallet, 0, self.appid)


class EntryNotFoundError(Exception):
    """Exception raised, when a requested entry does not exist."""
    pass


class ConnectionRefusedError(Exception):
    """Exception raised, when connecting to the session bus is not possible."""
    pass
