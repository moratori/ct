#!/usr/bin/env python3

import sys
import os
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

import logic.ctclient as client


class TestCTclient(unittest.TestCase):

    def __init__(self, *positional, **keyword):
        unittest.TestCase.__init__(self, *positional, **keyword)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_0(self):
        instance = client.CTclient(
            "https://ct.googleapis.com/logs/argon2021/", 10)

        self.assertTrue(instance.get_sth())
   
    def test_1(self):
        instance = client.CTclient(
            "https://ct.googleapis.com/logs/argon2021/", 10)

        self.assertTrue(instance.get_roots())

    def test_2(self):
        instance = client.CTclient(
            "https://ct.googleapis.com/logs/argon2021/", 10)

        self.assertTrue(instance.get_certificates(100, 103))

    def test_3(self):
        instance = client.CTclient(
            "https://ct.googleapis.com/logs/argon2021/", 10)

        self.assertTrue(instance.is_readable_server())

    def test_4(self):
        instance = client.CTclient(
            "https://ct.googleapis.com/logs/argon2021/", 10)

        self.assertFalse(instance.is_unreadable_server())
