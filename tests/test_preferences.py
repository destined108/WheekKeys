import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from wheekkeys.settings import Settings, load_settings, save_settings
from wheekkeys.models import builtin, export_model, import_model, load_model, available_models, builtin_models
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
            self.assertEqual([m.id for m in models], ['potato', 'mochi', imported.id])
            self.assertEqual(models[2].name, exported.name)
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

    def test_meal_threshold_boundaries_and_high_threshold_feeding(self):
        for threshold in (1, 1000):
            with self.subTest(threshold=threshold), TemporaryDirectory() as folder:
                path = Path(folder)/'settings.json'
                settings = Settings(threshold=threshold)
                save_settings(settings, path)
                self.assertEqual(load_settings(path).threshold, threshold)
                pet = Pet(threshold=threshold)
                pet.tick(0, threshold-1)
                self.assertEqual(pet.state, 'rest')
                pet.tick(0, 1)
                self.assertEqual(pet.state, 'run')
        for threshold in (0, 1001, 1.5, True):
            with self.subTest(invalid=threshold), self.assertRaises(ValueError):
                Settings(threshold=threshold).validate()

    def test_grass_growth_scales_with_large_threshold(self):
        skin = builtin().skin
        normal = render(Pet(grass=12, threshold=12), skin)
        high = render(Pet(grass=1000, threshold=1000), skin)
        self.assertEqual(normal.tobytes(), high.tobytes())
        halfway = render(Pet(grass=500, threshold=1000), skin)
        self.assertNotEqual(high.tobytes(), halfway.tobytes())

    def test_malformed_models_are_skipped_without_hiding_valid_models(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            export_model(builtin(), root/'valid')
            for i, data in enumerate(([], None, 'bad', 42,
                                      dict(name='Bad', poses=[], walk='walk.png', skin='skin.json'))):
                folder = root/f'bad-{i}'
                folder.mkdir()
                (folder/'model.json').write_text(json.dumps(data), encoding='utf-8')
            models, errors = available_models(root)
            self.assertEqual([model.id for model in models], ['potato', 'mochi', 'valid'])
            self.assertEqual(len(errors), 5)

    def test_builtin_mochi_is_available_without_any_user_models(self):
        from wheekkeys.i18n import Translator
        with TemporaryDirectory() as directory:
            models, errors = available_models(Path(directory)/'not-created')
            self.assertEqual([model.id for model in models], ['potato', 'mochi'])
            self.assertEqual(errors, [])
            mochi = models[1]
            self.assertEqual(Translator('en').model_name(mochi), 'Mochi')
            self.assertEqual(Translator('zh-Hans').model_name(mochi), '奶糖')
            self.assertEqual(Translator('zh-Hant').model_name(mochi), '奶糖')
            for state in ('rest', 'run', 'eat', 'return'):
                self.assertIsNotNone(render(Pet(state=state), mochi.skin, model=mochi).getbbox())
            self.assertNotEqual(render(Pet(), models[0].skin, model=models[0]).tobytes(),
                                render(Pet(), mochi.skin, model=mochi).tobytes())
            path = Path(directory)/'settings.json'
            save_settings(Settings(model='mochi'), path)
            self.assertEqual(load_settings(path).model, mochi.id)

    def test_builtin_models_load_from_packaged_resource_layout(self):
        from unittest.mock import patch
        from wheekkeys.art import ROOT
        import shutil
        with TemporaryDirectory() as directory:
            bundle = Path(directory)
            shutil.copytree(ROOT/'assets', bundle/'assets')
            shutil.copytree(ROOT/'skins', bundle/'skins')
            shutil.copytree(ROOT/'models/community/mochi', bundle/'models/community/mochi')
            with patch('wheekkeys.models.ROOT', bundle), patch('wheekkeys.art.ROOT', bundle):
                models = builtin_models()
                self.assertEqual([model.id for model in models], ['potato', 'mochi'])
                self.assertTrue(Path(models[1].poses).is_relative_to(bundle))
                for model in models:
                    self.assertIsNotNone(render(Pet(), model.skin, model=model).getbbox())
