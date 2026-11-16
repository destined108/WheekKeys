"""Create, check, preview and package WheekKeys data-only model packs."""
import argparse
import json
from pathlib import Path
import sys
from zipfile import ZipFile, ZIP_DEFLATED

# Works both in the repo and when this skill is installed in an agent's skill folder.
for candidate in (Path.cwd(), *Path(__file__).resolve().parents):
    if (candidate / 'wheekkeys' / 'models.py').is_file():
        sys.path.insert(0, str(candidate))
        break
else:
    raise SystemExit('Run this helper from the WheekKeys repository root.')

from PIL import Image
from wheekkeys.models import builtin, export_model, load_model
from wheekkeys.scene import Scene
from wheekkeys.art import render, load_skin


def check(folder):
    model = load_model(folder)
    for path in (model.poses, model.walk):
        with Image.open(path) as source:
            image = source.convert('RGBA')
        alpha = image.getchannel('A')
        if alpha.getextrema()[0] == 255:
            raise ValueError(f'{Path(path).name} must have a transparent background.')
        width = image.width // 4
        for index in range(4):
            cell = alpha.crop((index*width, 0, (index+1)*width, image.height))
            if cell.point(lambda value: 255 if value > 128 else 0).getbbox() is None:
                raise ValueError(f'{Path(path).name}: frame {index+1} is empty.')
    return model


def preview(folder):
    folder = Path(folder)
    model = check(folder)
    return render_preview(model, folder/'preview.gif', model.skin)


def render_preview(model, target, skin):
    target = Path(target)
    scene = Scene(demo=True)
    frames = []
    for _ in range(200):
        pet = scene.advance(.05)
        frames.append(render(pet, skin, '#182B27', model).convert('RGB'))
    target.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(target, save_all=True, append_images=frames[1:], duration=50, loop=0, optimize=True)
    return target


def preview_skin(path, output, model_folder=None):
    if Path(output).suffix.lower() != '.gif':
        raise ValueError('Palette preview output must end in .gif.')
    skin = load_skin(path)
    model = check(model_folder) if model_folder else builtin()
    return render_preview(model, output, skin)


def package(folder, output):
    folder, output = Path(folder).resolve(), Path(output).resolve()
    model = check(folder)
    if output.exists():
        raise ValueError(f'Output already exists: {output}')
    manifest = dict(name=model.name, poses='poses.png', walk='walk.png', skin='skin.json')
    source_manifest = json.loads((folder/'model.json').read_text(encoding='utf-8-sig'))
    files = {'poses.png': Path(model.poses), 'walk.png': Path(model.walk),
             'skin.json': (folder/source_manifest['skin']).resolve()}
    for name in ('README.md', 'README.zh-CN.md', 'LICENSE', 'preview.gif'):
        path = folder/name
        if path.is_file():
            if not path.resolve().is_relative_to(folder):
                raise ValueError(f'Pack attachment must stay inside its folder: {name}')
            files[name] = path
    if output in files.values() or output == folder/'model.json':
        raise ValueError('ZIP output must not replace a model resource.')
    output.parent.mkdir(parents=True, exist_ok=True)
    stream = output.open('xb')  # Fail without touching any concurrently created output.
    try:
        with stream, ZipFile(stream, 'w', compression=ZIP_DEFLATED) as archive:
            archive.writestr(f'{folder.name}/model.json', json.dumps(manifest, indent=2, ensure_ascii=False))
            for name, path in files.items():
                archive.write(path, f'{folder.name}/{name}')
    except Exception:
        output.unlink(missing_ok=True)
        raise
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest='command', required=True)
    init_parser = subparsers.add_parser('init', help='Copy the built-in layout template to a new folder')
    init_parser.add_argument('folder', type=Path)
    init_parser.add_argument('--name', required=True)
    for command in ('check', 'preview', 'package'):
        child = subparsers.add_parser(command)
        child.add_argument('folder', type=Path)
        if command == 'package':
            child.add_argument('--output', type=Path, required=True)
    palette_parser = subparsers.add_parser('preview-skin', help='Validate a palette and render its ten-second preview')
    palette_parser.add_argument('palette', type=Path)
    palette_parser.add_argument('--output', type=Path, required=True)
    palette_parser.add_argument('--model', type=Path, help='Custom model folder; defaults to Potato')
    args = parser.parse_args()
    try:
        if args.command == 'init':
            if not args.name.strip():
                raise ValueError('Name must not be empty.')
            model = builtin()
            model.name = args.name.strip()
            model.skin = dict(model.skin, name=model.name)
            export_model(model, args.folder)
            print(f'Template created: {args.folder}. Replace the artwork before sharing a new character.')
        elif args.command == 'check':
            model = check(args.folder)
            print(f'Valid model: {model.name}; 8 visible frames; transparent PNG sheets.')
        elif args.command == 'preview-skin':
            print(preview_skin(args.palette, args.output, args.model))
        elif args.command == 'preview':
            print(preview(args.folder))
        else:
            print(package(args.folder, args.output))
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()
