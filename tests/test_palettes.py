import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from wheekkeys.art import load_skin, render, COLOR_KEYS
from wheekkeys.core import Pet


class PaletteTests(unittest.TestCase):
    def test_utf8_names_load_under_a_non_utf8_windows_default(self):
        original_open = io.open
        def windows_open(file, mode='r', buffering=-1, encoding=None, errors=None,
                         newline=None, closefd=True, opener=None):
            if 'b' not in mode and encoding in (None, 'locale'):
                encoding = 'cp950'
            return original_open(file, mode, buffering, encoding, errors, newline, closefd, opener)
        with TemporaryDirectory() as directory:
            path = Path(directory)/'花色.json'
            data = dict(load_skin(), name='小白的花色')
            path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
            with patch('io.open', side_effect=windows_open):
                self.assertEqual(load_skin(path)['name'], data['name'])
            path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8-sig')
            self.assertEqual(load_skin(path)['name'], data['name'])

    def test_hex_case_never_changes_the_rendered_colors(self):
        original = load_skin()
        lower = dict(original, **{key: original[key].lower() for key in COLOR_KEYS})
        for state in ('rest', 'run', 'eat', 'return'):
            pet = Pet(state=state)
            self.assertEqual(render(pet, original).tobytes(), render(pet, lower).tobytes())
        with TemporaryDirectory() as directory:
            path = Path(directory)/'skin.json'
            path.write_text(json.dumps(lower), encoding='utf-8')
            self.assertEqual(load_skin(path), original)

    def test_invalid_palette_shapes_and_hex_values_are_rejected(self):
        with TemporaryDirectory() as directory:
            path = Path(directory)/'skin.json'
            valid = load_skin()
            for data in ([], None, {}, dict(valid, fur=None), dict(valid, fur='#+12345'), dict(valid, fur='#12345G')):
                path.write_text(json.dumps(data), encoding='utf-8')
                with self.subTest(data=data), self.assertRaises(ValueError):
                    load_skin(path)
