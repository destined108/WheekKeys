import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import sys
import unittest
from unittest.mock import patch, Mock
import tkinter as tk
from tkinter import ttk
from wheekkeys.__main__ import Application
from wheekkeys.settings import load_settings
from wheekkeys.models import builtin, export_model


def descendants(widget):
    for child in widget.winfo_children():
        yield child
        yield from descendants(child)


@unittest.skipUnless(sys.platform == 'win32' or os.environ.get('DISPLAY'), 'A graphical display is required')
class InterfaceTests(unittest.TestCase):
    def test_settings_model_switch_and_tray_commands(self):
        with TemporaryDirectory() as folder, patch.dict(os.environ, {'APPDATA': ''}):
            directory = Path(folder)/'user'
            tray = Mock()
            with patch('wheekkeys.__main__.user_directory', return_value=directory), \
                 patch('wheekkeys.settings.user_directory', return_value=directory), \
                 patch('wheekkeys.__main__.create_tray', return_value=tray):
                root = tk.Tk()
                app = Application(root, SimpleNamespace(demo=True, skin=None))
                # Provide the same queue bridge on Linux, where no tray is started.
                app.tray = tray
                try:
                    root.update()
                    app.open_settings()
                    root.update()
                    controls = [w for w in descendants(app.dialog) if isinstance(w, ttk.Spinbox)]
                    controls[0].set('25')
                    controls[1].set('1.5')
                    controls[2].set('.75')
                    save = next(w for w in descendants(app.dialog) if isinstance(w, ttk.Button) and w.cget('text') == 'Save')
                    save.invoke()
                    root.update()
                    self.assertEqual((app.settings.threshold, app.settings.speed, app.settings.scale), (25, 1.5, .75))
                    self.assertEqual(load_settings(directory/'settings.json'), app.settings)
                    exported = export_model(builtin(), Path(folder)/'custom')
                    with patch('wheekkeys.__main__.filedialog.askdirectory', return_value=str(Path(exported.poses).parent)):
                        app.import_model()
                    self.assertNotEqual(app.settings.model, 'potato')
                    self.assertEqual(app.model.id, app.settings.model)
                    app.commands.put(('model', 'potato'))
                    app.commands.put(('pause', None))
                    app.commands.put(('visibility', None))
                    app.frame()
                    self.assertTrue(app.hidden)
                    self.assertTrue(app.settings.paused)
                    self.assertEqual(app.model.id, 'potato')
                    app.toggle_visibility()
                    root.update()
                    self.assertEqual(root.state(), 'normal')
                finally:
                    app.quit()
                tray.stop.assert_called_once()
