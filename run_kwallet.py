#!/usr/bin/env python
# -*- coding: utf-8 -*-

from keyring import *

k = KWallet(u'pimme', u'personal')
k.open()
k.set_folder(u'Passwords')
print k.read_password(u'test')
m = k.read_map(u'vodafone')
print m[2:]
