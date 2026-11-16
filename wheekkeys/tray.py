"""Tray callbacks enqueue commands; only the Tk thread touches widgets."""
from .art import COLOR_KEYS, sprites
from .i18n import Translator, LANGUAGES, LANGUAGE_NAMES


def create_tray(model, get_models, get_settings, send, translator=None):
    import pystray
    t = translator or Translator()
    def action(command, value=None):
        return lambda icon, item: send((command, value))

    def item(label, *args, **kwargs):
        return pystray.MenuItem(lambda menu_item: t(label), *args, **kwargs)

    def language_menu():
        return tuple(pystray.MenuItem(
            (lambda item: t('Follow system')) if key == 'auto' else LANGUAGE_NAMES[key],
            action('language', key), radio=True,
            checked=lambda item, value=key: get_settings().language == value)
            for key in LANGUAGES)

    def models_menu():
        return tuple(pystray.MenuItem(
            lambda item, value=model: t.model_name(value), action('model', model.id), radio=True,
            checked=lambda item, key=model.id: get_settings().model == key)
            for model in get_models())

    menu = pystray.Menu(
        item('Show / hide pet', action('visibility'), default=True),
        item('Pet model', pystray.Menu(models_menu)),
        item('Import model…', action('import_model')),
        item('Export model template…', action('export_model')),
        item('Import colors…', action('import_skin')),
        item('Language', pystray.Menu(language_menu)),
        item('Settings…', action('settings')),
        item('Pause typing', action('pause'), checked=lambda item: get_settings().paused),
        item('Feed a little hay', action('feed')),
        pystray.Menu.SEPARATOR,
        item('Quit WheekKeys', action('quit')))
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
