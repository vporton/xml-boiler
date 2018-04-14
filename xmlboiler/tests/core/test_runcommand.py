import unittest

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
