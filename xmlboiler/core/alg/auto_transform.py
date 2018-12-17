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

from xmlboiler.core.alg.common import log_script_execution, AssetsExhausted
from xmlboiler.core.util.xml import myXMLParseString

# it skips scripts for which there is no interpreter
from xmlboiler.core.scripts.xml import Providers


class RealNextScript(object):
    def __init__(self, state, interpreters, xml_run_command=Providers.xml_run_command):
        self.state = state
        self.interpreters = interpreters
        self.xml_run_command = xml_run_command

    def step(self):
        while True:
            script = next(self.state.next_script)['script']
            interpreter_node = self.interpreters.find_interpreter(script.more.language,
                                                                  script.more.min_version,
                                                                  script.more.max_version)
            if interpreter_node is None:
                self.state.failed_scripts.add(script)
            else:
                log_script_execution(self.state, script)
                self.state.executed_scripts.add(script)

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


class AutomaticTranformation(object):
    def __init__(self, state, interpreter):
        self.state = state
        self.interpreter = interpreter

    def _step(self):
        all_namespaces = set()

        self.state.dom = myXMLParseString(self.state.xml_text)

        # depth-first search
        parents = [self.state.dom.documentElement]
        while parents:
            v = parents.pop()
            if v.namespaceURI is not None:
                all_namespaces.add(URIRef(v.namespaceURI))
            if v.attributes:
                for a in v.attributes.values():
                    if a.namespaceURI is not None:
                        all_namespaces.add(URIRef(a.namespaceURI))
            for w in v.childNodes:
                parents.append(w)

        # hack
        self.state.all_namespaces = frozenset(
            filter(lambda x: x not in(URIRef('http://www.w3.org/2000/xmlns/'),
                                      URIRef('http://www.w3.org/XML/1998/namespace')),  # TODO: Really exclude this?
                   all_namespaces))

        if self.state.all_namespaces <= self.state.opts.target_namespaces:
            return False  # The transformation finished!

        try:
            RealNextScript(self.state, self.interpreter).step()
        except StopIteration:
            try:
                next(self.state.download_algorithm)
            except StopIteration:
                raise AssetsExhausted()

        return True

    def run(self):
        while self._step():  # may raise AssetsExhausted
            pass


class Algorithms(containers.DeclarativeContainer):
    automatic_transformation = providers.Factory(AutomaticTranformation)
