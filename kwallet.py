# -*- coding: utf-8 -*-

import dbus
import binascii

class KWallet(object):
    def __init__(self, application, wallet=None):
        self.appid = application
        self.__bus = dbus.SessionBus()
        name = u'org.kde.kwalletd'
        object_path = u'/modules/kwalletd'
        self.__kw = self.__bus.get_object(name, object_path)
        interface = u'org.kde.KWallet'
        self.iface = dbus.Interface(self.__kw, dbus_interface=interface)
        if wallet:
            self.wallet = wallet
        else:
            self.wallet = self.iface.localWallet()

    def open(self):
        self.__handle = self.iface.open(self.wallet, 0, self.appid)

    def close(self):
        # TODO Write close function and implement context manager
        self.iface.close(self.__kw, True, self.appid)

    def get(self, key, field=u'password'):
        res = self.iface.readMap(self.__handle, self.__folder,
                                 key, self.appid,
                                 byte_arrays=True, utf8_strings=True)
        if res == 'None':
            raise EntryNotFoundError(u'Entry %s not found' % key)
        info = self._decode(res)
        return info[field]

    def set_folder(self, folder):
        if not self.iface.hasFolder(self.__handle, folder, self.appid):
            self.iface.createFolder(self.__handle, folder, self.appid)
        self.__folder = folder

    def set_value(self, key, value, field=u'password'):
        try:
            info = self.get(key, field)
        except (EntryNotFoundError, KeyError):
            info = {}
        info[field] = value
        info = self._encode(info)
        info = dbus.ByteArray(info)
        print repr(info)
        self.iface.writeMap(self.__handle, self.__folder, key, info, self.appid)

    def _decode(self, value):
        """Decode a dbus.ByteArray bsaed on a qmap.

        The first 4 bytes are the number of entries."""
        length = self._binary_to_int(value[:4])
        info = {}
        value = value[4:]
        for i in xrange(length):
            (key, length) = self._next_entry(value)
            value = value[length:]
            (data, length) = self._next_entry(value)
            value = value[length:]
            info[key] = data
        return info

    def _encode(self, value):
        data = []
        for (key, val) in value.items():
            data.append(key)
            data.append(val)
        length = (hex(len(value.keys())))[2:]
        enc = '00000000' + length
        enc = binascii.a2b_hex(enc[-8:])
        for d in data:
            length = self._calculate_length(d)
            enc += binascii.a2b_hex(length)
            for c in d:
                enc += '\x00' + c
        return enc
            
    def _binary_to_int(self, value, base=16):
        return int(binascii.b2a_hex(value), base)

    def _next_entry(self, value):
        length = self._binary_to_int(value[:4])
        data = value[4:length + 4]
        data = ''.join(x for x in data if x != '\x00')
        return (data, length + 4)

    def _calculate_length(self, data):
        length = (hex(len(data) * 2))[2:]
        length = '00000000' + length
        return length[-8:]



class EntryNotFoundError(Exception):
    pass
