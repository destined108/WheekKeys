import argparse
import ctypes
import sys
import time
import tkinter as tk
from PIL import ImageTk
from .core import Pet
from .art import load_skin, render

class KeyCounter:
    """Count rising edges only. Never translate keys into text or retain events."""
    def __init__(self):
        self.user32 = ctypes.windll.user32
        self.previous = set()

    def poll(self):
        # Exclude mouse buttons, modifiers and unused virtual-key slots.
        down = {k for k in range(8, 255)
                if k not in (16, 17, 18, 160, 161, 162, 163, 164, 165)
                and self.user32.GetAsyncKeyState(k) & 0x8000}
        count = len(down - self.previous)
        self.previous = down
        return count

def main():
    parser = argparse.ArgumentParser(description='Type to grow hay for your guinea pig.')
    parser.add_argument('--skin', help='Path to a palette JSON')
    parser.add_argument('--demo', action='store_true', help='Automatic ten-second loop; no global keyboard polling')
    args = parser.parse_args()
    if sys.platform != 'win32' and not args.demo:
        parser.error('Global keyboard mode requires Windows. Use --demo for an animation preview.')
    skin = load_skin(args.skin)
    root = tk.Tk()
    root.title('WheekKeys')
    root.overrideredirect(True)
    root.attributes('-topmost', True)
    transparent = '#ff00ff'
    root.configure(bg=transparent)
    if sys.platform == 'win32':
        root.attributes('-transparentcolor', transparent)
    root.geometry(f'640x224+{max(0, root.winfo_screenwidth()-660)}+{max(0, root.winfo_screenheight()-290)}')
    label = tk.Label(root, bg=transparent, borderwidth=0)
    label.pack()
    menu = tk.Menu(root, tearoff=False)
    menu.add_command(label='Feed a little hay', command=lambda: feed())
    menu.add_command(label='Quit WheekKeys', command=root.destroy)
    label.bind('<Button-3>', lambda e: menu.tk_popup(e.x_root, e.y_root))
    label.bind('<Button-1>', lambda e: setattr(root, '_drag', (e.x_root-root.winfo_x(), e.y_root-root.winfo_y())))
    label.bind('<B1-Motion>', lambda e: root.geometry(f'+{e.x_root-root._drag[0]}+{e.y_root-root._drag[1]}'))
    root.bind('<Escape>', lambda e: root.destroy())
    pet = Pet()
    counter = None if args.demo else KeyCounter()
    previous = time.monotonic()
    cycle = 0.0
    def feed():
        pet.tick(0, 12)
    def frame():
        nonlocal previous, cycle, pet
        now = time.monotonic()
        dt = min(.1, now-previous)
        previous = now
        before = cycle
        cycle += dt
        if args.demo and cycle >= 10:
            cycle, pet, before = 0., Pet(), 0.
        presses = (int(min(cycle, 2)*6)-int(min(before, 2)*6)) if args.demo else counter.poll()
        pet.tick(dt, presses)
        label.image = ImageTk.PhotoImage(render(pet, skin, transparent))
        label.configure(image=label.image)
        root.after(16, frame)
    frame()
    root.mainloop()

if __name__ == '__main__':
    main()
