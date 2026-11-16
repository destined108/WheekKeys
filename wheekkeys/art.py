"""Shared sprite renderer for the desktop pet and the actual demo GIF."""
import colorsys
from functools import lru_cache
import json
import math
import re
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_COLORS = ('#B97643', '#43352F', '#F6E5BD', '#D6958F', '#211F25')
COLOR_KEYS = ('fur', 'patch', 'cream', 'ear', 'eye')


def load_skin(path=None):
    data = json.loads(Path(path or ROOT / 'skins' / 'tricolor.json').read_text(encoding='utf-8-sig'))
    if not isinstance(data, dict):
        raise ValueError('Palette must be a JSON object.')
    for key in COLOR_KEYS:
        value = data.get(key)
        if not isinstance(value, str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', value):
            raise ValueError(f'{key} must be #RRGGBB')
        data[key] = value.upper()
    return data


@lru_cache(maxsize=16)
def sprites(palette, walking=False, poses_path=None, walk_path=None):
    """Load once; preserve the painted fur shading when applying custom palettes."""
    palette = tuple(value.upper() for value in palette)
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


def chewing_sprite(sprite, elapsed):
    """Move the lower muzzle one pixel; eyes, outline and paws stay fixed.

    The displacement fades to zero at the patch boundary, avoiding the seam
    caused by resizing a whole pixel-art character between 61 and 62 rows.
    """
    amount = (0, .6, 1., .6)[int(elapsed * 6) % 4]
    if not amount:
        return sprite
    result = sprite.copy()
    left, right = round(sprite.width*.64), round(sprite.width*.92)
    top, bottom = round(sprite.height*.62), round(sprite.height*.88)
    source, target = sprite.load(), result.load()
    for y in range(top, bottom):
        vertical = math.sin(math.pi * (y-top) / (bottom-top))
        for x in range(left, right):
            horizontal = math.sin(math.pi * (x-left) / (right-left))
            offset = round(amount * math.sqrt(max(0, vertical * horizontal)))
            target[x, y] = source[x, y-offset]
    return result


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
    # Never rescale the whole face to chew: that makes eyes and fur shimmer.
    if eating:
        sprite = chewing_sprite(sprite, pet.elapsed)
    if pet.state == 'return':
        sprite = sprite.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    ground = 94
    x = int(pet.x) - sprite.width // 2
    y = ground - sprite.height
    # Binary alpha avoids magenta fringes with Windows' color-key transparency.
    sprite = sprite.copy()
    sprite.putalpha(sprite.getchannel('A').point(lambda a: 255 if a >= 128 else 0))
    im.alpha_composite(sprite, (x, y))
    # Scale visual growth to the meal threshold and bound drawing work.
    visible_grass = min(24, math.ceil(pet.grass * 12 / pet.threshold))
    for i in range(visible_grass):
        gx = 250 + (i * 7 % 30)
        height = 4 + (i * 3 % 14)
        sway = int(math.sin(pet.elapsed*10+i)*2) if eating else 0
        d.line((gx, ground, gx + (i % 3 - 1)*4+sway, ground-height), fill='#72af55', width=2)
        d.line((gx, ground-3, gx+4+sway, ground-height+2), fill='#b7d878', width=2)
    if eating:
        mouth_x = x + round(sprite.width*.78)
        jaw_offset = round((0, .6, 1., .6)[int(pet.elapsed * 6) % 4])
        mouth_y = y + round(sprite.height*.74) + jaw_offset
        # Keep the stem attached to the mouth and shorten it as it is eaten.
        length = max(2, round(10 * (1-min(1, pet.elapsed / 2))))
        tip_y = mouth_y - 3 + int(phase)
        d.line((mouth_x, mouth_y, mouth_x+length, tip_y), fill='#95bf55', width=1)
    # The same visible feedback is shown for real taps and demo taps.
    lit = pet.key_flash > 0
    d.rounded_rectangle((246, 97, 263, 109), radius=2,
                        fill='#f6e5bd' if lit else '#33483e')
    d.text((250, 96), '+', fill='#33483e' if lit else '#b7d878')
    for i in range(12):
        d.rectangle((266+i*3, 101, 267+i*3, 106),
                    fill='#b7d878' if i < min(12, pet.grass * 12 / pet.threshold) else '#33483e')
    return im.resize((640, 224), Image.Resampling.NEAREST)
