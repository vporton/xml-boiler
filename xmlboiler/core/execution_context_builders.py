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


import logging
import locale
import gettext
import dependency_injector.containers as containers
import dependency_injector.providers as providers

from xmlboiler.core.data import Global
from .execution_context import ExecutionContext


def init_locale(lang=None):
    #locale.setlocale(locale.LC_ALL, '')  # TODO: call from your app
    try:
        if lang is None:
            lang = locale.getlocale()[0][0:2]
        file = Global.get_resource_stream("res/messages_%s.mo" % lang)
        trans = gettext.GNUTranslations(file)
    except (ValueError, IOError):
        logging.debug("Locale not found. Using default messages")
        trans = gettext.NullTranslations()
    #trans.set_output_charset()  # TODO
    return trans


def my_logger(name='main'):
    logger = providers.ThreadSafeSingleton(logging.getLogger)(name=name)
    logger.setLevel(logging.INFO)
    return logger

class Contexts(containers.DeclarativeContainer):
    default_logger = providers.Callable(my_logger)
    default_translations = providers.ThreadSafeSingleton(init_locale)
    execution_context = providers.Factory(ExecutionContext, logger=default_logger, translations=default_translations)


def context_for_logger(context, logger):
    return Contexts.execution_context(logger=logger, translations=context.translations)