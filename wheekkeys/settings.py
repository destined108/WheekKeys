"""Validated per-user preferences; never written into the installed application."""
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path


def user_directory():
    return Path(os.environ.get('APPDATA', Path.home() / '.config')) / 'WheekKeys'


@dataclass
class Settings:
    model: str = 'potato'
    skin: str = ''
    threshold: int = 12
    speed: float = 1.0
    scale: float = 1.0
    topmost: bool = True
    paused: bool = False
    x: int | None = None
    y: int | None = None

    def validate(self):
        if type(self.threshold) is not int or not 4 <= self.threshold <= 100:
            raise ValueError('Keys per meal must be an integer between 4 and 100.')
        for name in ('speed', 'scale'):
            value = getattr(self, name)
            if type(value) not in (int, float) or not .5 <= value <= 2:
                raise ValueError(f'{name.title()} must be between 0.5 and 2.0.')
        if any(type(getattr(self, k)) is not bool for k in ('topmost', 'paused')):
            raise ValueError('Invalid switch value.')
        if any(not isinstance(getattr(self, k), str) for k in ('model', 'skin')):
            raise ValueError('Invalid model or skin path.')
        if any(v is not None and type(v) is not int for v in (self.x, self.y)):
            raise ValueError('Invalid window position.')
        return self


def load_settings(path=None):
    path = Path(path) if path else user_directory() / 'settings.json'
    if not path.exists():
        return Settings()
    return Settings(**json.loads(path.read_text(encoding='utf-8'))).validate()


def save_settings(settings, path=None):
    settings.validate()
    path = Path(path) if path else user_directory() / 'settings.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(asdict(settings), indent=2), encoding='utf-8')
    temporary.replace(path)
