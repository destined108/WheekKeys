import unittest
from wheekkeys.scene import Scene

class SceneTests(unittest.TestCase):
    def test_live_taps_grow_grass_and_start_meal(self):
        scene = Scene()
        for i in range(12):
            scene.advance(.05, 1)
            self.assertEqual(scene.pet.grass, i+1)
            self.assertGreater(scene.pet.key_flash, 0)
        self.assertEqual(scene.pet.state, 'run')
        scene.advance(8)
        self.assertEqual((scene.pet.meals, scene.pet.state, scene.pet.grass), (1, 'rest', 0))

    def test_gif_and_window_timing_produce_identical_scenes(self):
        gif, window = Scene(demo=True), Scene(demo=True)
        for _ in range(200):
            gif.advance(.05)
            for _ in range(3):
                window.advance(1/60)
            self.assertEqual(gif.pet, window.pet)
        self.assertEqual(gif.pet.meals, 1)

    def test_demo_replays_same_cycle(self):
        scene = Scene(demo=True)
        scene.advance(2)
        first = vars(scene.pet).copy()
        scene.advance(10)
        self.assertEqual(vars(scene.pet), first)

    def test_pending_input_survives_short_render_frame(self):
        scene = Scene()
        scene.advance(.001, 2)
        self.assertEqual(scene.pet.grass, 0)
        scene.advance(.02)
        self.assertEqual(scene.pet.grass, 2)

    def test_sleep_gap_keeps_new_input_and_does_not_skip_meal(self):
        scene = Scene()
        scene.advance_live(8*3600, 12)
        self.assertEqual(scene.pet.state, 'run')
        self.assertEqual(scene.pet.meals, 0)
        self.assertGreater(scene.pet.key_flash, 0)
        self.assertLess(scene.step, 10)
        scene.advance_live(3600)
        self.assertEqual(scene.pet.meals, 0)
        for _ in range(500):
            scene.advance_live(1/60)
        self.assertEqual((scene.pet.state, scene.pet.meals), ('rest', 1))

    def test_slow_demo_finishes_return_before_reset(self):
        scene = Scene(demo=True)
        scene.speed = scene.pet.speed = .5
        scene.advance(10)
        self.assertEqual((scene.pet.state, scene.pet.meals), ('return', 1))
        for _ in range(400):
            state, x, meals, step = scene.pet.state, scene.pet.x, scene.pet.meals, scene.step
            scene.advance(1/60)
            if scene.step < step:
                self.assertEqual((state, x, meals), ('rest', 48, 1))
                break
        else:
            self.fail('Slow demo never restarted after completing its meal')
