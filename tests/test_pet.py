import unittest
from wheekkeys.core import Pet
from wheekkeys.art import load_skin, render, sprites, DEFAULT_COLORS

class PetTests(unittest.TestCase):
    def test_full_meal_returns_to_rest(self):
        p = Pet()
        states = set()
        for n in range(200):
            p.tick(.05, 1 if n < 36 and n % 3 == 0 else 0)
            states.add(p.state)
        self.assertEqual(states, {'rest', 'run', 'eat', 'return', 'settle'})
        self.assertEqual((p.state, p.grass, p.meals, p.x), ('rest', 0, 1, 48))

    def test_no_activity_no_food(self):
        p = Pet()
        for _ in range(200):
            p.tick(.05)
        self.assertEqual((p.state, p.meals), ('rest', 0))

    def test_grass_is_bounded(self):
        p = Pet()
        p.tick(0, 10000)
        self.assertEqual(p.grass, 24)
        p.tick(0, -100)
        self.assertEqual(p.grass, 24)

    def test_skins_render_all_states(self):
        for path in ('skins/tricolor.json', 'skins/template.json'):
            skin = load_skin(path)
            for state in ('rest', 'run', 'eat', 'return', 'settle'):
                image = render(Pet(state=state, grass=12), skin)
                self.assertEqual(image.size, (640, 224))
                self.assertIsNotNone(image.getbbox())

    def test_sprite_states_and_custom_palette(self):
        skin = load_skin()
        awake = render(Pet(state='run'), skin)
        asleep = render(Pet(state='rest'), skin)
        self.assertNotEqual(awake.tobytes(), asleep.tobytes())
        self.assertEqual(awake.getpixel((0, 0))[3], 0)
        custom = dict(skin, fur='#7197BF', patch='#405472')
        self.assertNotEqual(awake.tobytes(), render(Pet(state='run'), custom).tobytes())

    def test_walk_is_grounded_and_uses_distance(self):
        frames = sprites(DEFAULT_COLORS, walking=True)
        self.assertEqual(len(frames), 4)
        self.assertEqual({f.size for f in frames}, {(86, 62)})
        self.assertEqual(len({f.tobytes() for f in frames}), 4)
        skin = load_skin()
        # Time alone must not rotate/bounce or animate stationary feet.
        first = render(Pet(state='run', x=100, elapsed=0), skin)
        later = render(Pet(state='run', x=100, elapsed=.3), skin)
        self.assertEqual(first.tobytes(), later.tobytes())
        # All four placements keep the paws on the same ground line.
        for x in (48, 54, 60, 66):
            bounds = render(Pet(state='run', x=x), skin).getbbox()
            self.assertEqual(bounds[3], 188)

    def test_travel_eases_and_stops_at_destination(self):
        p = Pet(state='run')
        p.tick(.1)
        initial_step = p.x - 48
        p.tick(.9)
        before = p.x
        p.tick(.1)
        self.assertGreater(p.x - before, initial_step)
        p.tick(1.1)
        self.assertEqual((p.state, p.x), ('eat', 224))
        p.tick(2)
        p.tick(2.5)
        self.assertEqual((p.state, p.x), ('settle', 48))

if __name__ == '__main__':
    unittest.main()
