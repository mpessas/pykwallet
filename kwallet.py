# -*- coding: utf-8 -*-

import dbus

class KWallet(object):
    def __init__(self, application, wallet=None):
        self.appid = application
        self.__bus = dbus.SessionBus()
        name = u'org.kde.kwalletd'
        object_path = u'/modules/kwalletd'
        self.__kw = self.__bus.get_object(name, object_path)
        interface = u'org.kde.KWallet'
        self.iface = dbus.Interface(self.__kw, dbus_interface=interface)
        if wallet is None:
            self.wallet = self.iface.localWallet()
        else:
            self.wallet = wallet

    def open(self):
        self.__handle = self.iface.open(self.wallet, 0, self.appid)

    def close(self):
        # TODO Write close function and implement context manager
        self.iface.close(self.__kw, True, self.appid)

    def set_folder(self, folder):
        if not self.iface.hasFolder(self.__handle, folder, self.appid):
            self.iface.createFolder(self.__handle, folder, self.appid)
        self.__folder = folder

    def read_password(self, key):
        return self.iface.readPassword(self.__handle, self.__folder,
                                      key, self.appid, utf8_strings=True)

    def read_map(self, key):
        res = self.iface.readMap(self.__handle, self.__folder,
                                 key, self.appid,
                                 byte_arrays=True, utf8_strings=True)
        res = res.split('\x00\x00')
        return res[3]

    def get(self, key):
        self.iface.readMap(self.kw)
