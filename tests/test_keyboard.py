"""Test edge counting without accessing the host keyboard."""
import unittest
from unittest.mock import patch
from types import SimpleNamespace
from wheekkeys.__main__ import KeyCounter

class KeyboardTests(unittest.TestCase):
    def test_count_new_presses_not_holds_mouse_or_modifiers(self):
        down = set()
        api = SimpleNamespace(GetAsyncKeyState=lambda key: 0x8000 if key in down else 0)
        with patch('ctypes.windll', SimpleNamespace(user32=api), create=True):
            counter = KeyCounter()
        self.assertEqual(counter.poll(), 0)
        down.update((65, 66, 1, 16, 160))
        self.assertEqual(counter.poll(), 2)
        self.assertEqual(counter.poll(), 0)
        down.clear()
        self.assertEqual(counter.poll(), 0)
        self.assertEqual(counter.previous, set())
        down.add(65)
        self.assertEqual(counter.poll(), 1)

if __name__ == '__main__':
    unittest.main()
