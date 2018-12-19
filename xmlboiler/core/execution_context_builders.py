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


def init_locale(logger, lang=None):
    #locale.setlocale(locale.LC_ALL, '')  # call from your app
    try:
        if lang is None:
            lang = locale.getlocale()[0][0:2]
        file = Global.get_resource_stream("res/messages_%s.mo" % lang)
        trans = gettext.GNUTranslations(file)
    except (ValueError, IOError):
        logger.debug("Locale not found. Using default messages")
        trans = gettext.NullTranslations()
    #trans.set_output_charset()  # TODO
    return trans


def my_logger(name='main', level=logging.INFO):
    # logger = providers.ThreadSafeSingleton(logging.getLogger)(name=name)
    # logger = providers.Callable(logging.getLogger, name=name)()
    logger = logging.getLogger(name=name)
    logger.setLevel(level)

    # handler = logging.StreamHandler()
    # logger.addHandler(handler)

    return logger

class _BaseContexts(containers.DeclarativeContainer):
    logger = providers.Callable(my_logger)

class Contexts(_BaseContexts):
    default_translations = providers.ThreadSafeSingleton(init_locale, logger=_BaseContexts.logger)
    # 'unknown' is a hack not to modify an existing logger
    execution_context = providers.Factory(ExecutionContext, logger=_BaseContexts.logger)


def context_for_logger(context, logger):
    return Contexts.execution_context(logger=logger, translations=context.translations)
