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

# it skips scripts for which there is no interpreter
from xmlboiler.core.scripts.xml import Providers


class RealNextScript(object):
    def __init__(self, state, interpreters, xml_run_command=Providers.xml_run_command):
        self.state = state
        self.interpreters = interpreters
        self.xml_run_command = xml_run_command

    def step(self):
        while True:
            script = next(self.state.opts.next_script)['script']
            node = self.interpreters.find_interpreter(script.more.language, script.more.min_version,
                                                      script.more.max_version)
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

                # Check subprocess's exit code (what to do with _run_plain_text() as it spawns multiple commands?)
                # (It is not really necessary because we have an invalid XML then.)
                # Does not quite conform dependency injection pattern:
                new_xml_text = self.xml_run_command(self.state.opts.execution_context, script, self.interpreters, node, self.state.opts.command_runner).\
                    run(self.state.xml_text)
                if new_xml_text == self.state.xml_text:
                    msg = self.state.opts.execution_context.translate("Iteration stopped to avoid infinite loop.")
                    self.state.opts.error_logger.error(msg)
                self.state.xml_text = new_xml_text
                return
