import os
import unittest
from unittest.mock import patch, Mock
from types import SimpleNamespace
from wheekkeys.i18n import detect_language, windows_ui_language, Translator, ZH, ZH_HANT


class LanguageTests(unittest.TestCase):
    def test_locale_variants_and_english_fallback(self):
        for name, expected in (('zh_CN.UTF-8', 'zh-Hans'), ('zh-TW', 'zh-Hant'), ('zh_Hant_HK', 'zh-Hant'), ('zh_SG', 'zh-Hans'), ('zh', 'zh-Hans'), ('zh_MO', 'zh-Hant'), ('zh-Hans-TW', 'zh-Hans'), ('zh-Hant-CN', 'zh-Hant')):
            with self.subTest(name=name), patch('sys.platform', 'linux'), patch.dict(os.environ, {'LANG': name}, clear=True):
                self.assertEqual(detect_language(), expected)
        for name in ('en_US.UTF-8', 'ja_JP', 'de_DE', 'C', 'en:zh_CN'):
            with self.subTest(name=name), patch('sys.platform', 'linux'), patch.dict(os.environ, {'LANGUAGE': name}, clear=True):
                self.assertEqual(detect_language(), 'en')

    def test_windows_uses_display_language_not_regional_locale(self):
        for name in ('zh-Hans', 'zh-Hant', 'en'):
            with patch('sys.platform', 'win32'), patch.dict(os.environ, {'LANG': 'zh_CN'}, clear=True), \
                 patch('wheekkeys.i18n.windows_ui_language', return_value=name):
                self.assertEqual(detect_language(), name)

    def test_windows_primary_language_covers_chinese_variants(self):
        for langid, expected in ((0x0804, 'zh-Hans'), (0x0404, 'zh-Hant'), (0x0c04, 'zh-Hant'), (0x1004, 'zh-Hans'), (0x1404, 'zh-Hant'), (0x7c04, 'zh-Hant'), (0x7804, 'zh-Hans'), (0x0409, 'en'), (0x0411, 'en')):
            getter = Mock(return_value=langid)
            with patch('ctypes.WinDLL', return_value=SimpleNamespace(GetUserDefaultUILanguage=getter), create=True):
                self.assertEqual(windows_ui_language(), expected)

    def test_api_failure_and_missing_locale_fallback(self):
        with patch('sys.platform', 'win32'), patch('wheekkeys.i18n.windows_ui_language', side_effect=OSError), \
             patch.dict(os.environ, {}, clear=True), patch('locale.getlocale', return_value=(None, None)):
            self.assertEqual(detect_language(), 'en')

    def test_text_formatting_and_custom_names(self):
        zh = Translator('zh')
        self.assertEqual(zh('Save'), '保存')
        self.assertEqual(Translator('en')('Save'), 'Save')
        self.assertEqual(zh('Skipped invalid model: {error}', error='bad.json'), '已跳过无效的模型：bad.json')
        self.assertEqual(zh('Unknown {filename}'), 'Unknown {filename}')
        self.assertEqual(zh.model_name(SimpleNamespace(id='custom', name='My Cavy')), 'My Cavy')

    def test_traditional_catalog_is_complete(self):
        from string import Formatter
        self.assertEqual(set(ZH), set(ZH_HANT))
        for source, translated in ZH_HANT.items():
            fields = lambda message: {field for _, field, _, _ in Formatter().parse(message) if field}
            self.assertEqual(fields(source), fields(translated), source)
        self.assertEqual(Translator('zh-Hant')('Settings…'), '設定…')
        self.assertEqual(Translator('zh-Hant')('Save'), '儲存')
        self.assertEqual(Translator('zh-Hans')('Save'), '保存')
