"""Run from repository root: python -m docs.make_demo."""
from PIL import ImageDraw
from wheekkeys.art import render, load_skin
from wheekkeys.scene import Scene

scene = Scene(demo=True)
frames = []
skin = load_skin()
for n in range(200):
    pet = scene.advance(.05)
    frame = render(pet, skin, '#182B27').convert('RGB')
    d = ImageDraw.Draw(frame)
    title = 'TYPE A LITTLE' if n < 40 else 'HERE COMES POTATO' if pet.state == 'run' else 'CRUNCH, CRUNCH' if pet.state == 'eat' else 'BACK TO LOAF MODE'
    d.text((24, 8), title, fill='#F6E5BD', font_size=20)
    d.text((24, 34), 'WheekKeys / Type. Grow hay. Feed your cavy.', fill='#B8CDB8', font_size=14)
    frames.append(frame)
# Keep the versioned preview linked by README and chat distinct from older previews.
for destination in ('docs/demo.gif', 'docs/demo-chew-v4.gif'):
    frames[0].save(destination, save_all=True, append_images=frames[1:], duration=50, loop=0, optimize=True)
