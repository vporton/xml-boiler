#  Copyright (c) 2017 Victor Porton,
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


import logging
import locale
import gettext
import dependency_injector.containers as containers
import dependency_injector.providers as providers

from .execution_context import ExecutionContext


def init_locale(lang=locale.getlocale()[0][0:2]):
    #locale.setlocale(locale.LC_ALL, '')  # call from your app
    filename = "res/messages_%s.mo" % lang  # FIXME: filename
    try:
        trans = gettext.GNUTranslations(open(filename, "rb"))
    except IOError:
        logging.debug("Locale not found. Using default messages")
        trans = gettext.NullTranslations()
    #trans.set_output_charset()  # TODO
    return trans


class Contexts(containers.DeclarativeContainer):
    default_logger = providers.Singleton(logging.getLogger)
    default_translations = providers.Singleton(init_locale)
    execution_context = providers.Provider(logging=default_logger, translations=default_translations)