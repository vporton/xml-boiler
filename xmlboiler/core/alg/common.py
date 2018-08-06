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

from xmlboiler.core.interpreters.parse import interpreters
from xmlboiler.core.os_command.regular import regular_provider


# it skips scripts for which there is no interpreter
class RealNextScript(object):
    def __init__(self, state):
        self.state = state

    def step(self):
        while True:
            script = next(self.state.opts.next_script)
            # TODO: Support Web requests, etc.
            node = interpreters.parse.interpeters.find_interpreter(script.language, script.min_version, script.max_version)
            if node is not None:
                self.state.executed_scripts.append(script)
                # FIXME: What about .command_line?
                cmd = interpreters.parse.interpeters.construct_command_line(node, script.script_URL, script.params, bool(script.command_string))
                self.state.xml_text = regular_provider.run_pipe(cmd, self.state.xml_text)
                return
