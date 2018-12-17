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

class AssetsExhausted(StopIteration):
    pass


def log_script_execution(state, script):
    if script.more.script_url:
        state.opts.execution_context.logger.info(
            state.opts.execution_context.translations.gettext("Executed script {s}").format(
                s=script.more.script_url))
    else:
        state.opts.execution_context.logger.info(
            state.opts.execution_context.translations.gettext("Executed script for {s}").format(
                s=script.more.language))


def calculate_weight(weight_formula, script):
    if weight_formula == 'inverseofsum':
        return 1 / (script.base.preservance + script.base.stability + script.base.preference)
    elif weight_formula == 'sumofinverses':
        return 1 / script.base.preservance + 1 / script.base.stability + 1 / script.base.preference
    else:
        assert False
