import json
import os
from flask import session, request, current_app

class I18nService:
    def __init__(self, app=None):
        self.translations = {}
        self.default_locale = 'fr'
        self.supported_locales = ['fr', 'en']

        if app:
            self.init_app(app)

    def init_app(self, app):
        self.load_translations(app)

        @app.context_processor
        def inject_i18n():
            return dict(t=self.t, current_locale=self.get_locale())

    def load_translations(self, app):
        # Determine the path to the lang directory
        # Assuming app.root_path is the directory containing the app instance (root of repo in this case)
        # But let's check relative to this file first or CWD.

        # Option 1: os.getcwd() / 'lang' (Works if run from root)
        base_dir = os.getcwd()
        lang_dir = os.path.join(base_dir, 'lang')

        if not os.path.exists(lang_dir):
            # Fallback: maybe app.root_path?
            lang_dir = os.path.join(app.root_path, 'lang')

        for lang in self.supported_locales:
            file_path = os.path.join(lang_dir, f'{lang}.json')
            try:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.translations[lang] = json.load(f)
                else:
                    print(f"Warning: Language file {file_path} not found.")
                    self.translations[lang] = {}
            except Exception as e:
                print(f"Error loading language file {file_path}: {e}")
                self.translations[lang] = {}

    def get_locale(self):
        try:
            # 1. Check session
            if session and 'lang' in session and session['lang'] in self.supported_locales:
                return session['lang']

            # 2. Check header
            if request:
                best_match = request.accept_languages.best_match(self.supported_locales)
                if best_match:
                    return best_match
        except RuntimeError:
            # Outside of request context
            pass

        # 3. Default
        return self.default_locale

    def t(self, key, **kwargs):
        locale = self.get_locale()

        # Try current locale
        text = self.translations.get(locale, {}).get(key)

        # Fallback to default locale
        if text is None and locale != self.default_locale:
            text = self.translations.get(self.default_locale, {}).get(key)

        # Return key if not found
        if text is None:
            return key

        # Format if kwargs provided
        if kwargs:
            try:
                return text.format(**kwargs)
            except Exception:
                return text

        return text

i18n = I18nService()
