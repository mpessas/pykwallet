# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup (
    name = "pykwallet",
    version = "0.4",
    packages = ["pykwallet", "pykwallet.test"],
    author = "Apostolos Bessas",
    author_email = "mpessas@gmail.com",
    description = "Module to store and retrieve data from KWallet.",
    license = "GPL",
    test_suite = "pykwallet.test.test_pykwallet",
    requires = ["dbus", "scipy"],
)
