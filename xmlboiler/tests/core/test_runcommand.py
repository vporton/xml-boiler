#  Copyright (c) 2018 Victor Porton,
#  XML Boiler - http://freesoft.portonvictor.org
#
#  This file is part of XML Boiler.
#
#  XML Boiler is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.

import unittest

from xmlboiler.core.os_command.firejail import *
from xmlboiler.core.os_command.regular import *


class TestRunCommand(unittest.TestCase):
    def setUp(self):
        self.long = bytes(map(lambda i: i%3, range(1000000)))

    def do_test_ok(self, command, input):
        runner = regular_provider(timeout=None, timeout2=None)
        code, output = runner.run_pipe(command, input)
        self.assertEqual(code, 0)
        self.assertEqual(input, output)

    def test_cat_short(self):
        self.do_test_ok(['cat'], b"qwe")

    def test_cat_long(self):
        self.do_test_ok(['cat'], self.long)

    def test_dd_short(self):
        self.do_test_ok(["dd", "bs=100000", "count=10", "iflag=fullblock"], b"qwe")

    def test_dd_long(self):
        self.do_test_ok(["dd", "bs=100000", "count=10", "iflag=fullblock"], self.long)

    def test_sleep(self):
        with self.assertRaises(Timeout):
            runner = regular_provider(timeout=0.1, timeout2=1)
            runner.run_pipe(['sleep', '1000000'], b"")


class TestRunFirejailCommand(unittest.TestCase):
    def setUp(self):
        self.long = bytes(map(lambda i: i%3, range(1000000)))

    def do_test_ok(self, command, input):
        runner = firejail_provider(timeout=None, timeout2=None)
        code, output = runner.run_pipe(command, input)
        self.assertEqual(code, 0)
        self.assertEqual(input, output)

    def test_cat_short(self):
        self.do_test_ok(['cat'], b"qwe")

    def test_cat_long(self):
        self.do_test_ok(['cat'], self.long)

    def test_dd_short(self):
        self.do_test_ok(["dd", "bs=100000", "count=10", "iflag=fullblock"], b"qwe")

    def test_dd_long(self):
        self.do_test_ok(["dd", "bs=100000", "count=10", "iflag=fullblock"], self.long)

    def test_sleep(self):
        with self.assertRaises(Timeout):
            runner = firejail_provider(timeout=0.1, timeout2=1)
            runner.run_pipe(['sleep', '1000000'], b"")
