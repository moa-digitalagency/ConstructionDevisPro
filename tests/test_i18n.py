import unittest
from flask import Flask, session
from services.i18n_service import I18nService
import os

class I18nTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.secret_key = 'test'
        self.i18n = I18nService(self.app)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Ensure lang dir exists (it should as we created it)
        # But we need to make sure I18nService finds it.
        # In the test, os.getcwd() might be the repo root.

    def test_translations_loaded(self):
        with self.app.app_context():
            # Check if translations are loaded
            self.assertTrue('fr' in self.i18n.translations)
            self.assertTrue('en' in self.i18n.translations)

            # Check content
            self.assertEqual(self.i18n.translations['fr']['page_title_home'], 'Accueil')
            self.assertEqual(self.i18n.translations['en']['page_title_home'], 'Home')

    def test_translation_function(self):
        with self.app.test_request_context():
            # Default should be fr
            self.assertEqual(self.i18n.t('page_title_home'), 'Accueil')

            # Force EN in session
            session['lang'] = 'en'
            self.assertEqual(self.i18n.t('page_title_home'), 'Home')

            # Missing key returns key
            self.assertEqual(self.i18n.t('missing_key'), 'missing_key')

    def test_language_switch(self):
        # We need to register the route first as we did in app.py
        @self.app.route('/set_language/<lang>')
        def set_language(lang):
            if lang in self.i18n.supported_locales:
                session['lang'] = lang
            return 'OK'

        with self.client as c:
            # Default
            c.get('/')
            with c.session_transaction() as sess:
                self.assertIsNone(sess.get('lang'))

            # Switch to EN
            c.get('/set_language/en')
            with c.session_transaction() as sess:
                self.assertEqual(sess['lang'], 'en')

            # Switch to FR
            c.get('/set_language/fr')
            with c.session_transaction() as sess:
                self.assertEqual(sess['lang'], 'fr')

            # Switch to Invalid
            c.get('/set_language/es')
            with c.session_transaction() as sess:
                self.assertEqual(sess['lang'], 'fr') # Should remain fr

if __name__ == '__main__':
    unittest.main()
