# -*- coding: utf-8 -*-

import unittest
from pykwallet import KWallet, EntryNotFoundError


class TestKWallet(unittest.TestCase):

    def setUp(self):
        self.kw = KWallet("test_kwallet")
        self.kw.open()
        self.kw.set_folder('test_folder')

    def tearDown(self):
        self.kw.close()

    def test_get_error(self):
        entry = "test1"
        self.assertRaises(EntryNotFoundError, self.kw.get, entry)

    def test_get_success(self):
        entry = "test2"
        value = "test_value"
        self.kw.set(entry, value)
        self.assertEqual(self.kw.get(entry), value)

    def test_set(self):
        entry = "test"
        value = "test_password"
        self.kw.set(entry, value)
        self.assertEqual(self.kw.get(entry), value)

    def test_set_unicode(self):
        entry = u'δοκιμή'
        value = u'δοκιμή'
        self.kw.set(entry, value)
        self.assertEqual(self.kw.get(entry), value)


if __name__ == '__main__':
    unittest.main()
