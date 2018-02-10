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


class Container(containers.DeclarativeContainer):
    default_logger = providers.Singleton(logging.getLogger)
    default_translations = providers.Singleton(init_locale)
    execution_context = providers.Provider(logging=default_logger, translations=default_translations)