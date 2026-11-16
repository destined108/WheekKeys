import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from wheekkeys.settings import Settings, load_settings, save_settings
from wheekkeys.models import builtin, export_model, import_model, load_model, available_models
from wheekkeys.art import render
from wheekkeys.core import Pet


class PreferenceTests(unittest.TestCase):
    def test_preferences_round_trip(self):
        with TemporaryDirectory() as folder:
            path = Path(folder)/'settings.json'
            self.assertEqual(load_settings(path), Settings())
            settings = Settings(language='zh-Hant', threshold=25, speed=1.5, scale=.75, paused=True, x=100, y=200)
            save_settings(settings, path)
            self.assertEqual(load_settings(path), settings)
            self.assertFalse(path.with_suffix('.tmp').exists())

    def test_invalid_settings_do_not_replace_saved_values(self):
        with TemporaryDirectory() as folder:
            path = Path(folder)/'settings.json'
            save_settings(Settings(), path)
            for settings in (Settings(threshold=0), Settings(scale=float('nan')), Settings(speed=3), Settings(language='fr')):
                with self.assertRaises(ValueError):
                    save_settings(settings, path)
            self.assertEqual(load_settings(path), Settings())

    def test_model_template_import_survives_source_deletion(self):
        with TemporaryDirectory() as folder:
            folder = Path(folder)
            exported = export_model(builtin(), folder/'template')
            imported = import_model(folder/'template', folder/'models')
            import shutil
            shutil.rmtree(folder/'template')
            models, errors = available_models(folder/'models')
            self.assertEqual(errors, [])
            self.assertEqual([m.id for m in models], ['potato', imported.id])
            self.assertEqual(models[1].name, exported.name)
            self.assertEqual(render(Pet(), builtin().skin).tobytes(), render(Pet(), imported.skin, model=imported).tobytes())

    def test_invalid_model_cannot_escape_its_directory(self):
        with TemporaryDirectory() as folder:
            path = Path(folder)
            (path/'model.json').write_text(json.dumps(dict(name='Bad', poses='../outside.png', walk='walk.png', skin='skin.json')))
            with self.assertRaises(ValueError):
                load_model(path)

    def test_custom_threshold_and_speed_affect_behavior(self):
        pet = Pet(threshold=4, speed=2)
        pet.tick(0, 3)
        self.assertEqual(pet.state, 'rest')
        pet.tick(0, 1)
        self.assertEqual(pet.state, 'run')
        pet.tick(1.1)
        self.assertEqual((pet.state, pet.x), ('eat', 224))
        pet.tick(2)
        pet.tick(1.25)
        self.assertEqual((pet.state, pet.x), ('settle', 48))

    def test_speed_change_does_not_teleport(self):
        pet = Pet(state='run')
        pet.tick(.5)
        before = pet.x
        pet.speed = 2
        pet.tick(0)
        self.assertEqual(pet.x, before)
