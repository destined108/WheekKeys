import importlib.util
import os
import sys
import unittest
from unittest.mock import patch
from wheekkeys.models import builtin
from wheekkeys.settings import Settings
from wheekkeys.tray import create_tray
from wheekkeys.i18n import Translator


@unittest.skipUnless(importlib.util.find_spec('pystray'), 'Windows tray dependency is not installed')
class TrayTests(unittest.TestCase):
    def test_menu_dispatches_to_queue_and_reflects_settings(self):
        with patch.dict(os.environ, {'PYSTRAY_BACKEND': 'dummy'}):
            import pystray
        settings = Settings()
        commands = []
        models = [builtin()]
        with patch.object(pystray.Icon, 'run_detached'):
            icon = create_tray(models[0], lambda: models, lambda: settings, commands.append, translator=Translator('en'))
        items = {item.text: item for item in icon.menu.items}
        self.assertTrue(items['Pet model'].submenu.items[0].checked)
        self.assertFalse(items['Pause typing'].checked)
        settings.paused = True
        self.assertTrue(items['Pause typing'].checked)
        items['Settings…'](icon)
        items['Pet model'].submenu.items[0](icon)
        items['Show / hide pet'](icon)
        self.assertEqual(commands, [('settings', None), ('model', 'potato'), ('visibility', None)])
        # A newly imported model appears without restarting the tray.
        from dataclasses import replace
        models.append(replace(builtin(), id='custom', name='Custom'))
        self.assertEqual(len(items['Pet model'].submenu.items), 2)

    def test_chinese_menu_keeps_commands_language_independent(self):
        with patch.dict(os.environ, {'PYSTRAY_BACKEND': 'dummy'}):
            import pystray
        commands = []
        with patch.object(pystray.Icon, 'run_detached'):
            icon = create_tray(builtin(), lambda: [builtin()], Settings, commands.append, translator=Translator('zh'))
        items = {item.text: item for item in icon.menu.items}
        self.assertIn('设置…', items)
        self.assertNotIn('Settings…', items)
        self.assertEqual(items['宠物模型'].submenu.items[0].text, '土豆')
        items['设置…'](icon)
        self.assertEqual(commands, [('settings', None)])

    def test_language_menu_and_existing_labels_refresh(self):
        with patch.dict(os.environ, {'PYSTRAY_BACKEND': 'dummy'}):
            import pystray
        settings = Settings()
        commands = []
        translator = Translator('en')
        with patch.object(pystray.Icon, 'run_detached'):
            icon = create_tray(builtin(), lambda: [builtin()], lambda: settings, commands.append, translator=translator)
        language_item = next(item for item in icon.menu.items if item.text == 'Language')
        choices = language_item.submenu.items
        self.assertEqual([item.text for item in choices], ['Follow system', '简体中文', '繁體中文', 'English'])
        self.assertTrue(choices[0].checked)
        choices[2](icon)
        self.assertEqual(commands, [('language', 'zh-Hant')])
        settings.language = translator.language = 'zh-Hant'
        self.assertEqual(language_item.text, '語言')
        self.assertTrue(choices[2].checked)
        self.assertEqual(choices[0].text, '跟隨系統')
        self.assertIn('設定…', [item.text for item in icon.menu.items])
