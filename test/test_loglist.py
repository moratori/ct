#!/usr/bin/env python3

import sys
import os
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

import logic.loglist as loglist


class TestLogList(unittest.TestCase):

    def __init__(self, *positional, **keyword):
        unittest.TestCase.__init__(self, *positional, **keyword)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_0(self):
        ll = loglist.LogList()
        self.assertTrue(len(ll.loglist) == 0)
        ll.get_list("https://www.gstatic.com/ct/log_list/v2/log_list.json", 10)
        self.assertTrue(len(ll.loglist) > 0)

    def test_1(self):
        ll = loglist.LogList()
        self.assertTrue(len(ll.loglist) == 0)
        ll.get_list("https://www.gstatic.com/ct/log_list/v2/log_list.json", 10)

        self.assertTrue(len(ll.find_readable_server(3)) > 0)

    def test_2(self):
        ll = loglist.LogList()
        self.assertTrue(len(ll.loglist) == 0)
        ll.get_list("https://www.gstatic.com/ct/log_list/v2/log_list.json", 10)

        self.assertTrue(len(ll.find_unreadable_server(3)) > 0)
