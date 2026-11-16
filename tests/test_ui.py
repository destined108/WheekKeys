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
from wheekkeys.i18n import Translator


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
                 patch('wheekkeys.__main__.create_tray', return_value=tray), \
                 patch('wheekkeys.__main__.Translator', return_value=Translator('en')), \
                 patch('wheekkeys.__main__.detect_language', return_value='en'):
                root = tk.Tk()
                app = Application(root, SimpleNamespace(demo=True, skin=None))
                # Provide the same queue bridge on Linux, where no tray is started.
                app.tray = tray
                try:
                    root.update()
                    self.assertEqual([model.id for model in app.models], ['potato', 'mochi'])
                    app.select_model('mochi')
                    app.frame()
                    self.assertEqual(app.model.id, 'mochi')
                    self.assertEqual(load_settings(directory/'settings.json').model, 'mochi')
                    app.select_model('potato')
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

    def test_menus_and_settings_follow_detected_language(self):
        for language in ('zh-Hans', 'zh-Hant', 'en'):
            with self.subTest(language=language), TemporaryDirectory() as folder:
                directory = Path(folder)
                translator = Translator(language)
                with patch('wheekkeys.__main__.user_directory', return_value=directory), \
                     patch('wheekkeys.settings.user_directory', return_value=directory), \
                     patch('wheekkeys.__main__.create_tray', return_value=Mock()), \
                     patch('wheekkeys.__main__.Translator', return_value=translator), \
                     patch('wheekkeys.__main__.detect_language', return_value=language):
                    root = tk.Tk()
                    app = Application(root, SimpleNamespace(demo=True, skin=None))
                    try:
                        captured = []
                        with patch.object(tk.Menu, 'tk_popup', autospec=True, side_effect=lambda menu, x, y: captured.append(menu)):
                            app.popup(SimpleNamespace(x_root=10, y_root=10))
                        menu = captured[0]
                        labels = [menu.entrycget(i, 'label') for i in range(menu.index('end')+1) if menu.type(i) != 'separator']
                        self.assertIn(translator('Settings…'), labels)
                        self.assertIn(translator('Pet model'), labels)
                        models_menu = menu.nametowidget(menu.entrycget(0, 'menu'))
                        model_labels = [models_menu.entrycget(i, 'label') for i in range(2)]
                        self.assertIn(translator('Mochi'), model_labels)
                        app.open_settings()
                        root.update()
                        self.assertEqual(app.dialog.title(), translator('WheekKeys settings'))
                        buttons = [w.cget('text') for w in descendants(app.dialog) if isinstance(w, ttk.Button)]
                        self.assertIn(translator('Save'), buttons)
                        controls = [w for w in descendants(app.dialog) if isinstance(w, ttk.Spinbox)]
                        controls[0].set('not a number')
                        save = next(w for w in descendants(app.dialog) if isinstance(w, ttk.Button) and w.cget('text') == translator('Save'))
                        with patch('wheekkeys.__main__.messagebox.showerror') as error:
                            save.invoke()
                        self.assertEqual(error.call_args.args[0], translator('Check your settings'))
                        self.assertEqual(error.call_args.args[1], translator('Enter a whole number for keys per meal and numbers for speed and size.'))
                        # Language changes preserve unsaved settings and update the open window.
                        app.select_language('zh-Hant')
                        self.assertEqual(app.dialog.title(), 'WheekKeys 設定')
                        self.assertEqual(controls[0].get(), 'not a number')
                        self.assertEqual(save.cget('text'), '儲存')
                        self.assertEqual(load_settings(directory/'settings.json').language, 'zh-Hant')
                        app.select_language('auto')
                        self.assertEqual(app.t.language, language)
                        self.assertEqual(load_settings(directory/'settings.json').language, 'auto')
                    finally:
                        app.quit()

    def test_model_manager_cancel_delete_and_active_fallback(self):
        with TemporaryDirectory() as folder:
            directory = Path(folder)/'user'
            with patch('wheekkeys.__main__.user_directory', return_value=directory), \
                 patch('wheekkeys.settings.user_directory', return_value=directory), \
                 patch('wheekkeys.__main__.create_tray', return_value=Mock()):
                root = tk.Tk()
                app = Application(root, SimpleNamespace(demo=True, skin=None))
                try:
                    exported = export_model(builtin(), Path(folder)/'source')
                    with patch('wheekkeys.__main__.filedialog.askdirectory', return_value=str(Path(exported.poses).parent)):
                        app.import_model()
                    imported = app.model
                    app.open_settings()
                    root.update()
                    self.assertFalse(app.delete_button.instate(['disabled']))
                    with patch('wheekkeys.__main__.messagebox.askyesno', return_value=False):
                        app.delete_button.invoke()
                    self.assertTrue(Path(imported.poses).exists())
                    self.assertEqual(app.settings.model, imported.id)
                    with patch('wheekkeys.__main__.messagebox.askyesno', return_value=True), \
                         patch.object(app, 'persist', return_value=False):
                        app.delete_button.invoke()
                    self.assertTrue(Path(imported.poses).exists())
                    with patch('wheekkeys.__main__.messagebox.askyesno', return_value=True):
                        app.delete_button.invoke()
                    self.assertEqual(app.model.id, 'potato')
                    self.assertEqual(load_settings(directory/'settings.json').model, 'potato')
                    self.assertFalse(Path(imported.poses).parent.exists())
                    self.assertTrue(Path(exported.poses).exists())
                    self.assertEqual(list(app.model_list.get_children()), ['potato', 'mochi'])
                    self.assertTrue(app.delete_button.instate(['disabled']))
                    app.model_list.selection_set('mochi')
                    app.update_delete_button()
                    self.assertTrue(app.delete_button.instate(['disabled']))
                finally:
                    app.quit()
