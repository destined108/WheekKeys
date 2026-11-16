"""Self-contained model packs: four poses plus four walking frames."""
from dataclasses import dataclass
import json
from pathlib import Path
import shutil
from uuid import uuid4
from PIL import Image
from .art import ROOT, load_skin, sprites, COLOR_KEYS


@dataclass
class Model:
    id: str
    name: str
    skin: dict
    poses: str
    walk: str

    def frames(self, skin=None):
        palette = tuple((skin or self.skin)[k] for k in COLOR_KEYS)
        return sprites(palette, False, self.poses, self.walk), sprites(palette, True, self.poses, self.walk)


def builtin():
    return Model('potato', 'Potato / 土豆', load_skin(), str(ROOT/'assets/guinea-pig.png'), str(ROOT/'assets/guinea-pig-walk.png'))


def load_model(folder):
    folder = Path(folder).resolve()
    data = json.loads((folder/'model.json').read_text(encoding='utf-8-sig'))
    if not isinstance(data, dict):
        raise ValueError('Model manifest must be a JSON object.')
    if not isinstance(data.get('name'), str) or not data['name'].strip():
        raise ValueError('Model name is required.')
    paths = []
    for key in ('poses', 'walk', 'skin'):
        value = data.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError('Model file paths must be nonempty strings.')
        path = (folder / value).resolve()
        if not path.is_relative_to(folder):
            raise ValueError('All model files must be inside the model folder.')
        paths.append(path)
    for path in paths[:2]:
        with Image.open(path) as image:
            if image.format != 'PNG' or image.width % 4 or image.width > 8192 or image.height > 4096:
                raise ValueError('Sprite sheets must be PNG, four equal columns, at most 8192×4096.')
    model = Model(folder.name, data['name'].strip(), load_skin(paths[2]), str(paths[0]), str(paths[1]))
    model.frames()  # Verify every pose before replacing the active model.
    return model


def builtin_models():
    """The same resource paths work in a checkout and PyInstaller's bundle."""
    return [builtin(), load_model(ROOT/'models/community/mochi')]


def available_models(directory):
    models, errors = builtin_models(), []
    directory = Path(directory)
    if directory.exists():
        for folder in sorted(directory.iterdir()):
            if folder.is_dir():
                try:
                    models.append(load_model(folder))
                except (OSError, ValueError, KeyError, TypeError) as error:
                    errors.append(f'{folder.name}: {error}')
    return models, errors


def export_model(model, destination):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    try:
        shutil.copyfile(model.poses, destination/'poses.png')
        shutil.copyfile(model.walk, destination/'walk.png')
        (destination/'skin.json').write_text(json.dumps(model.skin, indent=2), encoding='utf-8')
        (destination/'model.json').write_text(json.dumps(dict(name=model.name, poses='poses.png', walk='walk.png', skin='skin.json'), indent=2, ensure_ascii=False), encoding='utf-8')
        return load_model(destination)
    except Exception:
        shutil.rmtree(destination)
        raise


def import_model(source, directory):
    model = load_model(source)
    return export_model(model, Path(directory)/('model-'+uuid4().hex[:12]))
