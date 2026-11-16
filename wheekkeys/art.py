"""Shared sprite renderer for the desktop pet and the actual demo GIF."""
import colorsys
from functools import lru_cache
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_COLORS = ('#B97643', '#43352F', '#F6E5BD', '#D6958F', '#211F25')
COLOR_KEYS = ('fur', 'patch', 'cream', 'ear', 'eye')


def load_skin(path=None):
    data = json.loads(Path(path or ROOT / 'skins' / 'tricolor.json').read_text())
    for key in COLOR_KEYS:
        value = data[key]
        if len(value) != 7 or value[0] != '#':
            raise ValueError(f'{key} must be #RRGGBB')
        int(value[1:], 16)
    return data


@lru_cache(maxsize=16)
def sprites(palette, walking=False, poses_path=None, walk_path=None):
    """Load once; preserve the painted fur shading when applying custom palettes."""
    filename = 'guinea-pig-walk.png' if walking else 'guinea-pig.png'
    path = (walk_path if walking else poses_path) or ROOT / 'assets' / filename
    with Image.open(path) as source:
        sheet = source.convert('RGBA')
    if palette != DEFAULT_COLORS:
        targets = [tuple(bytes.fromhex(c[1:])) for c in palette]
        pixels = []
        for r, g, b, a in sheet.getdata():
            if not a:
                pixels.append((r, g, b, a))
                continue
            h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
            if v < .14:
                key, baseline = 4, .1
            elif s < .35 and v > .65:
                key, baseline = 2, .9
            elif h < .045 and v > .45:
                key, baseline = 3, .7
            elif v < .4:
                key, baseline = 1, .28
            else:
                key, baseline = 0, .65
            shade = max(.35, min(1.4, v / baseline))
            pixels.append(tuple(min(255, int(c*shade)) for c in targets[key]) + (a,))
        sheet.putdata(pixels)
    frames = []
    cell = sheet.width // 4
    for i in range(4):
        frame = sheet.crop((i*cell, 0, (i+1)*cell, sheet.height))
        # Ignore barely visible edge pixels when finding the sprite silhouette.
        mask = frame.getchannel('A').point(lambda a: 255 if a > 128 else 0)
        bounds = mask.getbbox()
        if bounds is None:
            raise ValueError('Empty guinea pig sprite')
        frame = frame.crop(bounds)
        frames.append(frame)
    # One scale and fixed ground anchor across a cycle: never resize each pose
    # independently, which makes the torso pulse and the feet slide.
    scale = min(86 / max(f.width for f in frames), 62 / max(f.height for f in frames))
    aligned = []
    for frame in frames:
        frame = frame.resize((round(frame.width*scale), round(frame.height*scale)), Image.Resampling.LANCZOS)
        canvas = Image.new('RGBA', (86, 62))
        canvas.alpha_composite(frame, ((86-frame.width)//2, 62-frame.height))
        aligned.append(canvas)
    return tuple(aligned)


def render(pet, skin, background=(0, 0, 0, 0), model=None):
    im = Image.new('RGBA', (320, 112), background)
    d = ImageDraw.Draw(im)
    moving = pet.state in ('run', 'return')
    eating = pet.state == 'eat'
    sleeping = pet.state in ('rest', 'settle')
    index = 3 if sleeping else 2 if eating else 1 if moving else 0
    palette = tuple(skin[k] for k in COLOR_KEYS)
    paths = (model.poses, model.walk) if model else (None, None)
    if moving:
        distance = pet.x - 48 if pet.state == 'run' else 224 - pet.x
        index = int(max(0, distance) / 6) % 4
        sprite = sprites(palette, True, *paths)[index]
    else:
        sprite = sprites(palette, False, *paths)[index]
    phase = math.sin(pet.elapsed * (19 if moving else 13))
    # Only the painted legs change during travel; the torso stays grounded.
    if eating:
        sprite = sprite.resize((sprite.width, sprite.height - (1 if phase > 0 else 0)), Image.Resampling.NEAREST)
    if pet.state == 'return':
        sprite = sprite.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    ground = 94
    x = int(pet.x) - sprite.width // 2
    y = ground - sprite.height
    # Binary alpha avoids magenta fringes with Windows' color-key transparency.
    sprite = sprite.copy()
    sprite.putalpha(sprite.getchannel('A').point(lambda a: 255 if a >= 128 else 0))
    im.alpha_composite(sprite, (x, y))
    for i in range(pet.grass):
        gx = 250 + (i * 7 % 30)
        height = 4 + (i * 3 % 14)
        sway = int(math.sin(pet.elapsed*10+i)*2) if eating else 0
        d.line((gx, ground, gx + (i % 3 - 1)*4+sway, ground-height), fill='#72af55', width=2)
        d.line((gx, ground-3, gx+4+sway, ground-height+2), fill='#b7d878', width=2)
    if eating:
        mouth_x = int(pet.x) + sprite.width//2 - 9
        mouth_y = y + int(sprite.height*.69)
        d.line((mouth_x, mouth_y, mouth_x+10, mouth_y-3+int(phase*2)), fill='#95bf55', width=1)
    # The same visible feedback is shown for real taps and demo taps.
    lit = pet.key_flash > 0
    d.rounded_rectangle((246, 97, 263, 109), radius=2,
                        fill='#f6e5bd' if lit else '#33483e')
    d.text((250, 96), '+', fill='#33483e' if lit else '#b7d878')
    for i in range(12):
        d.rectangle((266+i*3, 101, 267+i*3, 106),
                    fill='#b7d878' if i < min(12, pet.grass * 12 / pet.threshold) else '#33483e')
    return im.resize((640, 224), Image.Resampling.NEAREST)
