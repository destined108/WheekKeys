"""Tray callbacks enqueue commands; only the Tk thread touches widgets."""
from .art import COLOR_KEYS, sprites


def create_tray(model, get_models, get_settings, send):
    import pystray
    def action(command, value=None):
        return lambda icon, item: send((command, value))

    def models_menu():
        return tuple(pystray.MenuItem(
            model.name, action('model', model.id), radio=True,
            checked=lambda item, key=model.id: get_settings().model == key)
            for model in get_models())

    menu = pystray.Menu(
        pystray.MenuItem('Show / hide pet', action('visibility'), default=True),
        pystray.MenuItem('Pet model', pystray.Menu(models_menu)),
        pystray.MenuItem('Import model…', action('import_model')),
        pystray.MenuItem('Export model template…', action('export_model')),
        pystray.MenuItem('Import colors…', action('import_skin')),
        pystray.MenuItem('Settings…', action('settings')),
        pystray.MenuItem('Pause typing', action('pause'), checked=lambda item: get_settings().paused),
        pystray.MenuItem('Feed a little hay', action('feed')),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem('Quit WheekKeys', action('quit')))
    icon = pystray.Icon('WheekKeys', tray_image(model), 'WheekKeys', menu)
    icon.run_detached()
    return icon


def tray_image(model, skin=None):
    from PIL import Image
    frames = sprites(tuple((skin or model.skin)[k] for k in COLOR_KEYS), False, model.poses, model.walk)
    image = frames[0].copy()
    image = image.crop(image.getbbox())
    image.thumbnail((60, 60), Image.Resampling.LANCZOS)
    canvas = Image.new('RGBA', (64, 64))
    canvas.alpha_composite(image, ((64-image.width)//2, (64-image.height)//2))
    return canvas
