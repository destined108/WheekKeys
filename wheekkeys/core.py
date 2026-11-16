"""Deterministic animation model; no keyboard data enters this module."""
from dataclasses import dataclass

@dataclass
class Pet:
    state: str = 'rest'
    grass: int = 0
    elapsed: float = 0
    x: float = 48
    meals: int = 0
    key_flash: float = 0

    def tick(self, dt: float, presses: int = 0):
        self.key_flash = .3 if presses > 0 else max(0, self.key_flash - dt)
        self.grass = min(24, self.grass + max(0, presses))
        self.elapsed += dt
        if self.state == 'rest' and self.grass >= 12:
            self.state, self.elapsed = 'run', 0
        elif self.state == 'run':
            t = min(1, self.elapsed / 2.2)
            self.x = 48 + 176 * t*t*(3-2*t)
            if self.x == 224:
                self.state, self.elapsed = 'eat', 0
        elif self.state == 'eat' and self.elapsed >= 2.0:
            self.grass = max(0, self.grass - 24)
            self.meals += 1
            self.state, self.elapsed = 'return', 0
        elif self.state == 'return':
            t = min(1, self.elapsed / 2.5)
            self.x = 224 - 176 * t*t*(3-2*t)
            if self.x == 48:
                self.state, self.elapsed = 'settle', 0
        elif self.state == 'settle' and self.elapsed >= .7:
            self.state, self.elapsed = 'rest', 0
