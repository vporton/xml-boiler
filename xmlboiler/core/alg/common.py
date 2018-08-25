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
import sys

from xmlboiler.core.os_command.regular import regular_provider


# it skips scripts for which there is no interpreter
from xmlboiler.core.scripts.xml import XMLRunCommand


class RealNextScript(object):
    def __init__(self, state, interpreters):
        self.state = state
        self.interpreters = interpreters

    def step(self):
        while True:
            script = next(self.state.opts.next_script)['script']  # TODO: ['script'] here is a hack
            # TODO: Support Web requests, etc.
            node = self.interpreters.find_interpreter(script.more.language, script.more.min_version, script.more.max_version)
            if node is None:
                self.state.failed_scripts.add(script)
            else:
                if script.more.script_url:
                    self.state.opts.execution_context.logger.info(
                        self.state.opts.execution_context.translations.gettext("Executed script {s}").format(s=script.more.script_url))
                else:
                    self.state.opts.execution_context.logger.info(
                        self.state.opts.execution_context.translations.gettext("Executed script for {s}").format(s=script.more.language))
                self.state.executed_scripts.add(script)

                cmd = self.interpreters.construct_command_line(node,
                                                               script.more.script_url if script.more.script_url else script.more.command_string,
                                                               script.more.params,
                                                               not bool(script.more.script_url))
                # TODO: Check subprocess's exit code
                new_xml_text = XMLRunCommand(script, self.interpreters).run(self.state.xml_text)  # TODO: Use proper dependency injection
                if new_xml_text == self.state.xml_text:
                    # TODO: Don't write to stderr, use a generic interfact
                    sys.stderr.write("Iteration stopped to avoid infinite loop.\n")  # TODO: Localization
                self.state.xml_text = new_xml_text
                return
