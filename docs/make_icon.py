"""Generate the Windows executable icon from the bundled character."""
from wheekkeys.models import builtin
from wheekkeys.tray import tray_image

if __name__ == '__main__':
    tray_image(builtin()).resize((256, 256)).save('assets/wheekkeys.ico', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (256, 256)])
