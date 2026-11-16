"""Count transitions without accessing the host keyboard."""
import unittest
import sys
from wheekkeys.keyboard import PressAccumulator, KeyCounter

class KeyboardTests(unittest.TestCase):
    def test_short_taps_between_frames_are_not_lost(self):
        counter = PressAccumulator()
        for _ in range(4):
            counter.event(65, True)
            counter.event(65, False)
        self.assertEqual(counter.drain(), 4)
        self.assertEqual(counter.drain(), 0)
        self.assertEqual(counter.down, set())

    def test_holds_mouse_and_modifiers(self):
        counter = PressAccumulator()
        for key in (65, 66, 1, 16, 160, 91):
            counter.event(key, True)
        for _ in range(10):
            counter.event(65, True)
        self.assertEqual(counter.drain(), 2)
        counter.event(65, False)
        counter.event(65, True)
        self.assertEqual(counter.drain(), 1)

    @unittest.skipUnless(sys.platform == 'win32', 'Native Windows hook required')
    def test_native_hook_starts_and_stops(self):
        counter = KeyCounter()
        try:
            self.assertTrue(counter.thread.is_alive())
            self.assertIsNone(counter.error)
        finally:
            counter.close()
        self.assertFalse(counter.thread.is_alive())

if __name__ == '__main__':
    unittest.main()
