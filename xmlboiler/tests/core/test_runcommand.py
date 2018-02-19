import unittest

from xmlboiler.core.os_command.regular import *

class TestRunCommand(unittest.TestCase):
    def setUp(self):
        self.long = bytes(map(lambda i: i%3, range(1000000)))

    def do_test_ok(self, command, input):
        code, output = RegularCommandRunner.run_pipe(command, input, timeout=None, timeout2=None)
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
