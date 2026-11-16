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
