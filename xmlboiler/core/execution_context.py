# Basic facilities for all kinds of procedures.
# Currently contains logging and localization.

class ExecutionContext(object):
    def __init__(self, logger, translations):
        """
        :param logger: logger
        :param translations: usually should be gettext.GNUTranslations
        """
        self.logger = logger
        self.translations = translations
