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


def stub_stdin(testcase_inst, inputs):
    stdin = sys.stdin

    def cleanup():
        sys.stdin = stdin

    testcase_inst.addCleanup(cleanup)
    sys.stdin = StringIO(inputs)


def stub_stdout(testcase_inst):
    stdout = sys.stdout

    def cleanup():
        sys.stdout = stdout

    testcase_inst.addCleanup(cleanup)
    sys.stdout = TextIOWrapper(BytesIO(), sys.stdout.encoding)


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

    def test_run1(self):
        # stub_stdin(self, Global.get_resource_bytes("tests/core/data/xml/xinclude.xml"))
        stub_stdout(self)
        command_line.main(['chain',
                           Global.get_filename("tests/core/data/xml/xinclude.xml"),
                           '-u',
                           'http://portonvictor.org/ns/trans/precedence-include',
                           '-s',
                           'doc1'])
        self.assertEqual(sys.stdout.buffer.getvalue(), TestUtility.XInclude_output)

    def test_run2(self):
        # stub_stdin(self, Global.get_resource_bytes("tests/core/data/xml/xinclude.xml"))
        stub_stdout(self)
        command_line.main(['chain',
                           Global.get_filename("tests/core/data/xml/xinclude.xml"),
                           '-u',
                           'http://portonvictor.org/ns/trans/precedence-include',
                           '-s',
                           'doc2'])
        self.assertEqual(sys.stdout.buffer.getvalue(), TestUtility.XInclude_output)

    def test_run3(self):
        # stub_stdin(self, Global.get_resource_bytes("tests/core/data/xml/xinclude.xml"))
        stub_stdout(self)
        command_line.main(['chain',
                           Global.get_filename("tests/core/data/xml/comment.xml"),
                           '-u',
                           'http://portonvictor.org/ns/trans/precedence-include',
                           '-s',
                           'doc1'])
        self.assertEqual(sys.stdout.buffer.getvalue(), TestUtility.comment_output)

    def test_run4(self):
        # stub_stdin(self, Global.get_resource_bytes("tests/core/data/xml/xinclude.xml"))
        stub_stdout(self)
        command_line.main(['chain',
                           Global.get_filename("tests/core/data/xml/comment.xml"),
                           '-u',
                           'http://portonvictor.org/ns/trans/precedence-include',
                           '-s',
                           'doc2'])
        self.assertEqual(sys.stdout.buffer.getvalue(), TestUtility.comment_output)
