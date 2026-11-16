import importlib.util
import os
import sys
import unittest
from unittest.mock import patch
from wheekkeys.models import builtin
from wheekkeys.settings import Settings
from wheekkeys.tray import create_tray


@unittest.skipUnless(importlib.util.find_spec('pystray'), 'Windows tray dependency is not installed')
class TrayTests(unittest.TestCase):
    def test_menu_dispatches_to_queue_and_reflects_settings(self):
        with patch.dict(os.environ, {'PYSTRAY_BACKEND': 'dummy'}):
            import pystray
        settings = Settings()
        commands = []
        models = [builtin()]
        with patch.object(pystray.Icon, 'run_detached'):
            icon = create_tray(models[0], lambda: models, lambda: settings, commands.append)
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
