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

# This is an object which receives bytes and produces bytes
from xmlboiler.core.os_command.regular import regular_provider
from xmlboiler.core.rdf_format.asset import CommandScriptInfo


class _RunScriptCommand(object):
    def __init__(self, script, interpreters, interpreter, command_runner, params=None):
        self.script = script
        self.interpreters = interpreters
        self.interpreter = interpreter
        self.command_runner = command_runner
        if not params:
            self.params = script.more.params

    def run(self, input: bytes, params) -> bytes:
        assert isinstance(self.script.more, CommandScriptInfo) and \
               (self.script.more.script_url is not None or self.script.more.command_string is not None)

        args = self.interpreters.construct_command_line(self.interpreter, self.script.more.script_url, params, inline=False)

        return self.command_runner.run_pipe(args, input)[1]


class _RunInlineCommand(object):
    def __init__(self, script, interpreters, interpreter, command_runner, params=None):
        self.script = script
        self.interpreters = interpreters
        self.interpreter = interpreter
        self.command_runner = command_runner
        if not params:
            self.params = script.more.params

    def run(self, input: bytes, params) -> bytes:
        assert isinstance(self.script.more, CommandScriptInfo) and \
               (self.script.more.script_url is None or self.script.more.command_string is not None)

        args = self.interpreters.construct_command_line(self.interpreter, self.script.more.command_string, params, inline=True)

        return self.command_runner.run_pipe(args, input)[1]


# TODO: WebService
class RunCommand(object):
    def __init__(self, script, interpreters, interpreter, command_runner):
        assert isinstance(script.more, CommandScriptInfo)
        if script.more.script_url:
            self.impl = _RunScriptCommand(script, interpreters, interpreter, command_runner)
        else:
            self.impl = _RunInlineCommand(script, interpreters, interpreter, command_runner)

    def run(self, input: bytes, params) -> bytes:
        return self.impl.run(input, params)
