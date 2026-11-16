"""Fixed-step playback shared by the live window, --demo and GIF export."""
from .core import Pet

STEP = 1 / 60
DEMO_STEPS = 600
MAX_LIVE_DT = .1


class Scene:
    def __init__(self, demo=False):
        self.demo = demo
        self.threshold, self.speed = 12, 1.0
        self.pet = Pet()
        self.step = 0
        self.remainder = 0.
        self.pending = 0

    def advance_live(self, dt, presses=0):
        """Resume gently after sleep/dialog stalls; keep newly received presses."""
        return self.advance(min(MAX_LIVE_DT, max(0, dt)), presses)

    def advance(self, dt, presses=0):
        self.pending += max(0, presses)
        self.remainder += max(0, dt)
        while self.remainder + 1e-9 >= STEP:
            self.remainder -= STEP
            if (self.demo and self.step >= DEMO_STEPS and self.pet.state == 'rest'
                    and self.pet.meals > 0 and not self.pet.grass and not self.pending):
                self.pet, self.step = Pet(threshold=self.threshold, speed=self.speed), 0
            self.step += 1
            # Twelve taps over two seconds, exactly the same for GIF and window.
            count = (min(self.step, 120)*self.threshold//120 - min(self.step-1, 120)*self.threshold//120) if self.demo else 0
            count += self.pending
            self.pending = 0
            self.pet.tick(STEP, count)
        return self.pet
