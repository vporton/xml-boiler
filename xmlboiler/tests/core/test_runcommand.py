import unittest

from xmlboiler.core.os_command.regular import *

class TestRunCommand(unittest.TestCase):
    def test_cat_short(self):
        input = b"qwe"
        output = RegularCommandRunner.run_pipe(['cat'], input, timeout=None, timeout2=None)
        self.assertEqual(input, output)
