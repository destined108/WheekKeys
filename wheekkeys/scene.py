"""Fixed-step playback shared by the live window, --demo and GIF export."""
from .core import Pet

STEP = 1 / 60
DEMO_STEPS = 600


class Scene:
    def __init__(self, demo=False):
        self.demo = demo
        self.pet = Pet()
        self.step = 0
        self.remainder = 0.
        self.pending = 0

    def advance(self, dt, presses=0):
        self.pending += max(0, presses)
        self.remainder += max(0, dt)
        while self.remainder + 1e-9 >= STEP:
            self.remainder -= STEP
            if self.demo and self.step == DEMO_STEPS:
                self.pet, self.step = Pet(), 0
            self.step += 1
            # Twelve taps over two seconds, exactly the same for GIF and window.
            count = int(self.step <= 120 and self.step % 10 == 0) if self.demo else self.pending
            self.pending = 0
            self.pet.tick(STEP, count)
        return self.pet
