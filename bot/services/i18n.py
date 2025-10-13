from bot.locales import LOCALES

DEFAULT_LANGUAGE = 'en'

class I18n:
    def __init__(self, language: str = DEFAULT_LANGUAGE):
        self.language = language if language in LOCALES else DEFAULT_LANGUAGE
    
    def get(self, key: str, **kwargs) -> str:
        """Get translation for key"""
        text = LOCALES[self.language].get(key, LOCALES[DEFAULT_LANGUAGE].get(key, key))
        if kwargs:
            text = text.format(**kwargs)
        return text
    
    def __call__(self, key: str, **kwargs) -> str:
        """Shorthand for get()"""
        return self.get(key, **kwargs)

def get_user_language(language_code: str) -> str:
    """Get user language from Telegram language code"""
    if language_code and language_code.startswith('ru'):
        return 'ru'
    elif language_code and language_code.startswith('cs'):
        return 'cs'
    return 'en'

