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
import contextlib
from io import StringIO, BytesIO, TextIOWrapper

import xmlboiler.command_line.command
from xmlboiler.core.data import Global
from xmlboiler.tests.core.xml_test import XmlTest


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
    # stdin = sys.stdin
    # stdout = sys.stdout
    # try:
    #     sys.stdin = TextIOWrapper(BytesIO(), sys.stdin.encoding)
    #     sys.stdout = TextIOWrapper(BytesIO(), sys.stdout.encoding)
    #     yield
    # finally:
    #     sys.stdin = stdin
    #     sys.stdout = stdout
    # with contextlib.redirect_stdout(TextIOWrapper(BytesIO(), sys.stdin.encoding)), \
    #      contextlib.redirect_stderr(TextIOWrapper(BytesIO(), sys.stderr.encoding)):
    #     yield
    with contextlib.redirect_stdout(TextIOWrapper(BytesIO(), sys.stdin.encoding)):
        yield


def setup_with_context_manager(testcase, cm):
    """Use a contextmanager to setUp a test case."""
    val = cm.__enter__()
    testcase.addCleanup(cm.__exit__, None, None, None)
    return val


class TestUtility(XmlTest):
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

    def command(self, args):
        ret = xmlboiler.command_line.command.main(args)
        self.assertTrue(ret == 0)

    def do_run_xinlude(self, order, next_script_mode):
        self.command(['-r', order,
                      '-s', next_script_mode,
                      '-i', Global.get_filename("tests/core/data/xml/xinclude.xml"),
                      'chain',
                      '-u', 'http://portonvictor.org/ns/trans/precedence-include'])
        self.assertXmlEqual(sys.stdout.buffer.getvalue(), TestUtility.XInclude_output)

    def do_run_comment(self, order, next_script_mode):
        self.command(['-r', order,
                      '-s', next_script_mode,
                      '-i', Global.get_filename("tests/core/data/xml/comment.xml"),
                      'chain',
                      '-u', 'http://portonvictor.org/ns/trans/precedence-comment'])
        self.assertXmlEqual(sys.stdout.buffer.getvalue(), TestUtility.comment_output)

    def do_run_comment_script(self, order, next_script_mode):
        self.command(['-r', order,
                      '-s', next_script_mode,
                      '-i', Global.get_filename("tests/core/data/xml/comment.xml"),
                      'script', 'http://portonvictor.org/ns/trans/comment#script-xslt'])
        self.assertXmlEqual(sys.stdout.buffer.getvalue(), TestUtility.comment_output)

    def do_run_comment_transform(self, order, next_script_mode):
        self.command(['-r', order,
                      '-s', next_script_mode,
                      '-i', Global.get_filename("tests/core/data/xml/comment.xml"),
                      'transform', 'http://portonvictor.org/ns/trans/comment#transformer'])
        self.assertXmlEqual(sys.stdout.buffer.getvalue(), TestUtility.comment_output)

    def test_run(self):
        # stub_stdin(self, Global.get_resource_bytes("tests/core/data/xml/xinclude.xml"))
        for func in [self.do_run_xinlude, self.do_run_comment, self.do_run_comment_script, self.do_run_comment_transform]:
            for next_script_mode in ['doc']:
                for order in ['breadth', 'depth']:
                    with self.subTest(func=func.__name__, next_script=next_script_mode, order=order):
                        with capture_stdin_and_stdout():
                            func(order, next_script_mode)

    def test_syntax(self):
        for next_script_mode in ['doc']:
            for order in ['breadth', 'depth']:
                with self.subTest(next_script=next_script_mode, order=order):
                    with capture_stdin_and_stdout():
                        self.command(['-r', order,
                                      '-s', next_script_mode,
                                      '-i', Global.get_filename("tests/core/data/xml/syntax.xml"),
                                      'chain',
                                      '-t', 'http://www.w3.org/1999/xhtml',
                                      '-n', 'error'])
                        # sys.stdout.buffer.write(b'<pre>...')
                        self.assertRegex(sys.stdout.buffer.getvalue().decode('utf-8'), r'<pre>')

    def test_avoid_infinite_loop(self):
        with capture_stdin_and_stdout():
            ret = xmlboiler.command_line.command.main(
                ['-i', Global.get_filename("tests/core/data/xml/wrong.xml"),
                 'c',
                 '-u', 'http://portonvictor.org/ns/trans/precedence-comment'])
            self.assertTrue(ret != 0)
            self.assertEqual(sys.stdout.buffer.getvalue().decode('utf-8'), "")

    def test_doc(self):
        with capture_stdin_and_stdout():
            self.command(['-r', 'breadth',
                          '-i', Global.get_filename("doc/index.html"),
                          'chain',
                          '-t', 'http://www.w3.org/1999/xhtml',
                          '-n', 'error'])
            breadth = sys.stdout.buffer.getvalue()
        with capture_stdin_and_stdout():
            self.command(['-r', 'depth',
                          '-i', Global.get_filename("doc/index.html"),
                          'chain',
                          '-t', 'http://www.w3.org/1999/xhtml',
                          '-n', 'error'])
            depth = sys.stdout.buffer.getvalue()
        self.assertXmlEqual(breadth, depth)

    def test_nodownload(self):
        with capture_stdin_and_stdout():
            self.command(['-r', 'none',
                          '-s', 'doc',
                          '-p', 'http://portonvictor.org/ns/comment',
                          '-i', Global.get_filename("tests/core/data/xml/comment.xml"),
                          'chain',
                          '-u', 'http://portonvictor.org/ns/trans/precedence-comment'])
            self.assertXmlEqual(sys.stdout.buffer.getvalue(), TestUtility.comment_output)

    def test_installed_packages(self):
        for installed in ['package', 'executable', 'both']:
            with self.subTest(installed=installed):
                with capture_stdin_and_stdout():
                    self.command(['--software',
                                  installed,
                                  '-i', Global.get_filename("tests/core/data/xml/comment.xml"),
                                  'chain',
                                  '-u', 'http://portonvictor.org/ns/trans/precedence-comment'])
                    self.assertXmlEqual(sys.stdout.buffer.getvalue(), TestUtility.comment_output)
