import argparse
import sys
import time
import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk
from .scene import Scene
from .keyboard import KeyCounter
from .art import load_skin, render

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
    scene = Scene(demo=args.demo)
    try:
        counter = None if args.demo else KeyCounter()
    except RuntimeError as error:
        messagebox.showerror('WheekKeys', str(error), parent=root)
        root.destroy()
        return

    def quit_pet():
        if counter:
            counter.close()
        root.destroy()

    menu.entryconfigure('Quit WheekKeys', command=quit_pet)
    root.protocol('WM_DELETE_WINDOW', quit_pet)
    root.bind('<Escape>', lambda e: quit_pet())
    previous = time.monotonic()
    def feed():
        scene.pending += 12
    def frame():
        nonlocal previous
        now = time.monotonic()
        dt = now-previous
        previous = now
        try:
            pet = scene.advance(dt, 0 if counter is None else counter.poll())
        except RuntimeError as error:
            messagebox.showerror('WheekKeys', str(error), parent=root)
            quit_pet()
            return
        label.image = ImageTk.PhotoImage(render(pet, skin, transparent))
        label.configure(image=label.image)
        root.after(16, frame)
    frame()
    root.mainloop()

if __name__ == '__main__':
    main()
