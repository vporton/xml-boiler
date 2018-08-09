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

import os
import sys
import unittest
import contextlib
from io import StringIO, BytesIO, TextIOWrapper

from xmlboiler import command_line
from xmlboiler.core.data import Global


@contextlib.contextmanager
def change_dir(new_dir):
    """
    Change directory, and then change back.
    """
    old_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield os.getcwd()
    finally:
        os.chdir(old_dir)


@contextlib.contextmanager
def capture_stdin_and_stdout():
    stdin = sys.stdin
    stdout = sys.stdout
    try:
        sys.stdin  = TextIOWrapper(BytesIO(), sys.stdin.encoding)
        sys.stdout = TextIOWrapper(BytesIO(), sys.stdout.encoding)
        yield
    finally:
        sys.stdin = stdin
        sys.stdout = stdout


def setup_with_context_manager(testcase, cm):
    """Use a contextmanager to setUp a test case."""
    val = cm.__enter__()
    testcase.addCleanup(cm.__exit__, None, None, None)
    return val


class TestUtility(unittest.TestCase):
    XInclude_output = b'<?xml version="1.0"?>' + b"\n" + \
                      b'<y xmlns:xi="http://www.w3.org/2001/XInclude">' + b"\n" + \
                      b'    <x/>' + b"\n" + \
                      b'</y>' + b"\n"
    comment_output = b'<?xml version="1.0"?>' + b"\n" + \
                     b'<x>' + b"\n" + \
                     b'    ' + b"\n" + \
                     b'</x>' + b"\n"

    def setUp(self):
        self.v = setup_with_context_manager(self, change_dir(Global.get_filename("tests/core/data/xml")))

    def test_run_xinlude(self):
        # stub_stdin(self, Global.get_resource_bytes("tests/core/data/xml/xinclude.xml"))
        for next_script_mode in ['doc1', 'doc2']:
            with capture_stdin_and_stdout():
                command_line.main(['chain',
                                   Global.get_filename("tests/core/data/xml/xinclude.xml"),
                                   '-u',
                                   'http://portonvictor.org/ns/trans/precedence-include',
                                   '-s',
                                   next_script_mode])
                self.assertEqual(sys.stdout.buffer.getvalue(), TestUtility.XInclude_output, "for %s" % next_script_mode)

    def test_run_comment(self):
        # stub_stdin(self, Global.get_resource_bytes("tests/core/data/xml/comment.xml"))
        for next_script_mode in ['doc1', 'doc2']:
            with capture_stdin_and_stdout():
                command_line.main(['chain',
                                   Global.get_filename("tests/core/data/xml/comment.xml"),
                                   '-u',
                                   'http://portonvictor.org/ns/trans/precedence-include',
                                   '-s',
                                   next_script_mode])
                self.assertEqual(sys.stdout.buffer.getvalue(), TestUtility.comment_output, "for %s" % next_script_mode)
