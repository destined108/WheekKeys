import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile
from PIL import Image
from wheekkeys.models import builtin, export_model, load_model

SCRIPT = Path(__file__).resolve().parents[1]/'.agents/skills/create-guinea-pig/scripts/model_pack.py'
spec = importlib.util.spec_from_file_location('model_pack_skill', SCRIPT)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


class ModelSkillTests(unittest.TestCase):
    def test_template_preview_zip_and_reimport(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            pack = root/'my-cavy'
            export_model(builtin(), pack)
            self.assertEqual(helper.check(pack).name, builtin().name)
            preview = helper.preview(pack)
            with Image.open(preview) as image:
                duration = 0
                for i in range(image.n_frames):
                    image.seek(i)
                    duration += image.info['duration']
                self.assertEqual(duration, 10000)
            (pack/'.env').write_text('private-local-data')
            output = helper.package(pack, root/'pet.zip')
            with ZipFile(output) as archive:
                self.assertEqual(set(archive.namelist()), {f'my-cavy/{name}' for name in ('model.json', 'poses.png', 'walk.png', 'skin.json', 'preview.gif')})
                archive.extractall(root/'unpacked')
            self.assertEqual(load_model(root/'unpacked/my-cavy').name, builtin().name)
            before = output.read_bytes()
            with self.assertRaises(ValueError):
                helper.package(pack, output)
            self.assertEqual(output.read_bytes(), before)

    def test_rejects_opaque_and_empty_frames(self):
        with TemporaryDirectory() as folder:
            pack = Path(folder)/'pet'
            export_model(builtin(), pack)
            Image.new('RGBA', (400, 100), 'white').save(pack/'walk.png')
            with self.assertRaisesRegex(ValueError, 'transparent'):
                helper.check(pack)
            image = Image.new('RGBA', (400, 100))
            from PIL import ImageDraw
            draw = ImageDraw.Draw(image)
            for i in range(3):
                draw.rectangle((i*100+10, 10, i*100+70, 80), fill='white')
            image.save(pack/'walk.png')
            with self.assertRaises(ValueError):
                helper.check(pack)

    def test_palette_preview_uses_user_colors_without_changing_source(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            palette = dict(builtin().skin, fur='#6699BB', patch='#344466')
            source = root/'skin.json'
            source.write_text(json.dumps(palette))
            before = source.read_bytes()
            output = helper.preview_skin(source, root/'previews/skin.gif')
            self.assertEqual(source.read_bytes(), before)
            with Image.open(output) as image:
                self.assertEqual(image.size, (640, 224))
                self.assertGreater(image.n_frames, 1)
            with self.assertRaises(ValueError):
                helper.preview_skin(source, source)
            self.assertEqual(source.read_bytes(), before)
            palette['fur'] = 'invalid'
            source.write_text(json.dumps(palette))
            with self.assertRaises(ValueError):
                helper.preview_skin(source, root/'invalid.gif')
            self.assertFalse((root/'invalid.gif').exists())
