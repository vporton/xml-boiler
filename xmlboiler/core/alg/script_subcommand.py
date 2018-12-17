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
from dependency_injector import containers, providers
from rdflib import URIRef

from xmlboiler.core.alg.common import AssetsExhausted


class ChainFilter(object):
    def __init__(self, script_url, state, interpreter):
        self.script_url = script_url
        self.state = state
        self.interpreter = interpreter

    def run(self):
        while True:
            script = self.state.scripts_hash.get(URIRef(self.script_url))
            if script:
                interpreter_node = self.interpreters.find_interpreter(script.more.language,
                                                                      script.more.min_version,
                                                                      script.more.max_version)
                # Check subprocess's exit code (what to do with _run_plain_text() as it spawns multiple commands?)
                # (It is not really necessary because we have an invalid XML then.)
                # Does not quite conform dependency injection pattern:
                new_xml_text = self.xml_run_command(self.state.opts.execution_context,
                                                    script,
                                                    self.interpreters,
                                                    interpreter_node,
                                                    self.state.opts.command_runner).\
                    run(self.state.xml_text)
                if new_xml_text == self.state.xml_text:
                    msg = self.state.opts.execution_context.translations.gettext("Iteration stopped to avoid infinite loop.")
                    self.state.opts.error_logger.error(msg)
                    raise AssetsExhausted()  # TODO: It is correct exception?
                self.state.xml_text = new_xml_text
                return
            else:
                try:
                    next(self.state.download_algorithm)
                except StopIteration:
                    raise AssetsExhausted()


class Algorithms(containers.DeclarativeContainer):
    chain_filter = providers.Factory(ChainFilter)
