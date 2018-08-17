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
from xmlboiler.core.interpreters.parse import interpreters
from xmlboiler.core.os_command.regular import regular_provider
from xmlboiler.core.rdf_format.asset import CommandScriptInfo


class _RunScriptCommand(object):
    def __init__(self, script, params=None):
        self.script = script
        self.interpreters = interpreters
        if not params:
            self.params = script.params

    def run(self, input: bytes) -> bytes:
        assert isinstance(self.script, CommandScriptInfo) and \
               self.script.script_URL is not None and self.script.command_string is None

        node = self.interpreters.find_interpreter(self.script.language, self.script.min_version, self.script.max_version)
        args = self.interpreters.construct_command_line(node, self.script.script_URL, self.params, inline=False)

        # TODO: Use dependency injection
        return regular_provider.run_pipe(args, input)


class _RunInlineCommand(object):
    def __init__(self, script):
        self.script = script
        self.interpreters = interpreters

    def run(self, input: bytes) -> bytes:
        assert isinstance(self.script, CommandScriptInfo) and \
               self.script.script_URL is None and self.script.command_string is not None

        node = self.interpreters.find_interpreter(self.script.language, self.script.min_version, self.script.max_version)
        args = self.interpreters.construct_command_line(node, self.script.command_string, self.params, inline=True)

        # TODO: Use dependency injection
        return regular_provider.run_pipe(args, input)


# TODO: WebService
class RunCommand(object):
    def __init__(self, script, interpreters):
        assert isinstance(script, CommandScriptInfo)
        if script.script_URL:
            self.impl = _RunScriptCommand(script)
        else:
            self.impl = _RunInlineCommand(script)

    def run(self, input: bytes) -> bytes:
        return self.impl.run(input)
