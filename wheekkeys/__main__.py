import argparse
from dataclasses import replace
from pathlib import Path
from queue import Empty, SimpleQueue
import shutil
import sys
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from uuid import uuid4
from PIL import Image, ImageTk
from .scene import Scene
from .keyboard import KeyCounter
from .art import load_skin, render
from .models import available_models, export_model, import_model
from .settings import Settings, load_settings, save_settings, user_directory
from .tray import create_tray, tray_image


class Application:
    def __init__(self, root, args):
        self.root, self.args = root, args
        self.directory = user_directory()
        self.models, errors = available_models(self.directory/'models')
        warnings = [f'Skipped invalid model: {e}' for e in errors]
        try:
            self.settings = load_settings()
        except (OSError, ValueError, TypeError) as error:
            self.settings = Settings()
            warnings.append(f'Could not load saved settings. Using defaults.\n{error}')
        self.model = next((m for m in self.models if m.id == self.settings.model), self.models[0])
        if self.model.id != self.settings.model:
            warnings.append('The saved model is unavailable. Using Potato.')
            self.settings.model = self.model.id
        self.skin = self.model.skin
        if args.skin or self.settings.skin:
            try:
                self.skin = load_skin(args.skin or self.settings.skin)
            except (OSError, ValueError, KeyError, TypeError) as error:
                warnings.append(f'Could not load colors. Using model colors.\n{error}')
                self.settings.skin = ''
        self.scene = Scene(demo=args.demo)
        self.configure_pet()
        self.counter = None
        self.tray = None
        self.commands = SimpleQueue()
        self.hidden = False
        self.closed = False
        self.dialog = None
        self.transparent = '#ff00ff'
        root.title('WheekKeys')
        root.overrideredirect(True)
        root.configure(bg=self.transparent)
        if sys.platform == 'win32':
            root.attributes('-transparentcolor', self.transparent)
        self.label = tk.Label(root, bg=self.transparent, borderwidth=0)
        self.label.pack()
        self.window_icon = ImageTk.PhotoImage(tray_image(self.model, self.skin))
        root.iconphoto(True, self.window_icon)
        self.position_window()
        self.label.bind('<Button-3>', self.popup)
        self.label.bind('<Button-1>', self.drag_start)
        self.label.bind('<B1-Motion>', self.drag_move)
        self.label.bind('<ButtonRelease-1>', self.drag_end)
        root.bind('<Escape>', lambda event: self.quit())
        root.protocol('WM_DELETE_WINDOW', self.quit)
        self.previous = time.monotonic()
        try:
            self.counter = None if args.demo else KeyCounter()
            if sys.platform == 'win32':
                try:
                    self.tray = create_tray(self.model, lambda: self.models, lambda: self.settings,
                                            self.commands.put)
                except Exception as error:
                    warnings.append(f'Tray icon could not start. The pet right-click menu is still available.\n{error}')
            for warning in warnings:
                messagebox.showwarning('WheekKeys', warning, parent=root)
            self.frame()
        except Exception:
            self.quit()
            raise

    def configure_pet(self):
        self.scene.threshold, self.scene.speed = self.settings.threshold, self.settings.speed
        self.scene.pet.threshold = self.settings.threshold
        self.scene.pet.speed = self.settings.speed

    def position_window(self):
        width, height = round(640*self.settings.scale), round(224*self.settings.scale)
        screen_w, screen_h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        x = self.settings.x if self.settings.x is not None else screen_w-width-20
        y = self.settings.y if self.settings.y is not None else screen_h-height-66
        x, y = max(0, min(x, screen_w-width)), max(0, min(y, screen_h-height))
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        self.root.attributes('-topmost', self.settings.topmost)

    def persist(self, settings):
        try:
            save_settings(settings)
        except (OSError, ValueError) as error:
            messagebox.showerror('Could not save settings', str(error), parent=self.root)
            return False
        self.settings = settings
        return True

    def refresh_tray(self):
        self.window_icon = ImageTk.PhotoImage(tray_image(self.model, self.skin))
        self.root.iconphoto(True, self.window_icon)
        if self.tray:
            self.tray.icon = tray_image(self.model, self.skin)
            self.tray.update_menu()

    def select_model(self, key):
        model = next(m for m in self.models if m.id == key)
        if self.persist(replace(self.settings, model=key, skin='')):
            self.model, self.skin = model, model.skin
            self.refresh_tray()

    def popup(self, event):
        menu = tk.Menu(self.root, tearoff=False)
        model_menu = tk.Menu(menu, tearoff=False)
        self.model_var = tk.StringVar(value=self.settings.model)
        for model in self.models:
            model_menu.add_radiobutton(label=model.name, variable=self.model_var, value=model.id,
                                      command=lambda key=model.id: self.select_model(key))
        model_menu.add_separator()
        model_menu.add_command(label='Import model…', command=self.import_model)
        model_menu.add_command(label='Export model template…', command=self.export_template)
        menu.add_cascade(label='Pet model', menu=model_menu)
        menu.add_command(label='Import colors…', command=self.import_skin)
        menu.add_command(label='Settings…', command=self.open_settings)
        self.pause_var = tk.BooleanVar(value=self.settings.paused)
        menu.add_checkbutton(label='Pause typing', variable=self.pause_var, command=self.toggle_pause)
        if self.tray:
            menu.add_command(label='Hide pet', command=self.toggle_visibility)
        menu.add_command(label='Feed a little hay', command=self.feed)
        menu.add_separator()
        menu.add_command(label='Quit WheekKeys', command=self.quit)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def feed(self):
        self.scene.pending += self.settings.threshold

    def toggle_pause(self):
        if self.persist(replace(self.settings, paused=not self.settings.paused)) and self.tray:
            self.tray.update_menu()

    def toggle_visibility(self):
        if not self.tray:
            return  # Never leave an invisible pet without a way to restore it.
        self.hidden = not self.hidden
        self.root.withdraw() if self.hidden else self.root.deiconify()

    def import_model(self):
        folder = filedialog.askdirectory(title='Choose a model folder containing model.json', parent=self.root)
        if not folder:
            return
        try:
            model = import_model(folder, self.directory/'models')
            self.models.append(model)
            self.select_model(model.id)
        except (OSError, ValueError, KeyError, TypeError) as error:
            messagebox.showerror('Cannot import model', str(error), parent=self.root)

    def export_template(self):
        parent = filedialog.askdirectory(title='Choose where to save the model template', parent=self.root)
        if not parent:
            return
        try:
            target = Path(parent)/('WheekKeys-model-'+uuid4().hex[:6])
            export_model(self.model, target)
            messagebox.showinfo('Model template saved', str(target), parent=self.root)
        except (OSError, ValueError) as error:
            messagebox.showerror('Cannot export template', str(error), parent=self.root)

    def import_skin(self):
        path = filedialog.askopenfilename(title='Choose a palette', filetypes=[('Palette JSON', '*.json')], parent=self.root)
        if not path:
            return
        try:
            skin = load_skin(path)
            self.model.frames(skin)
            folder = self.directory/'skins'
            folder.mkdir(parents=True, exist_ok=True)
            target = folder/(uuid4().hex+'.json')
            shutil.copyfile(path, target)
            if self.persist(replace(self.settings, skin=str(target))):
                self.skin = skin
                self.refresh_tray()
        except (OSError, ValueError, KeyError, TypeError) as error:
            messagebox.showerror('Cannot import colors', str(error), parent=self.root)

    def open_settings(self):
        if self.dialog and self.dialog.winfo_exists():
            self.dialog.lift()
            return
        dialog = self.dialog = tk.Toplevel(self.root)
        dialog.title('WheekKeys settings')
        dialog.resizable(False, False)
        dialog.attributes('-topmost', True)
        box = ttk.Frame(dialog, padding=20)
        box.grid()
        values = {}
        for row, (name, title, low, high, increment) in enumerate((
                ('threshold', 'Key presses per meal', 4, 100, 1),
                ('speed', 'Movement speed (×)', .5, 2, .1),
                ('scale', 'Display size (×)', .5, 2, .1))):
            ttk.Label(box, text=title).grid(row=row, column=0, sticky='w', pady=6, padx=(0, 20))
            values[name] = tk.StringVar(value=str(getattr(self.settings, name)))
            ttk.Spinbox(box, from_=low, to=high, increment=increment, textvariable=values[name], width=8).grid(row=row, column=1)
        topmost = tk.BooleanVar(value=self.settings.topmost)
        paused = tk.BooleanVar(value=self.settings.paused)
        ttk.Checkbutton(box, text='Keep pet above other windows', variable=topmost).grid(row=3, columnspan=2, sticky='w', pady=6)
        ttk.Checkbutton(box, text='Pause typing interaction', variable=paused).grid(row=4, columnspan=2, sticky='w', pady=6)
        ttk.Label(box, text='Changes take effect when you save.').grid(row=5, columnspan=2, pady=8)
        def save():
            try:
                settings = replace(self.settings, threshold=int(values['threshold'].get()),
                                   speed=float(values['speed'].get()), scale=float(values['scale'].get()),
                                   topmost=topmost.get(), paused=paused.get()).validate()
            except ValueError as error:
                messagebox.showerror('Check your settings', str(error), parent=dialog)
                return
            if self.persist(settings):
                self.configure_pet()
                self.position_window()
                if self.tray:
                    self.tray.update_menu()
                dialog.destroy()
        buttons = ttk.Frame(box)
        buttons.grid(row=6, columnspan=2, sticky='e', pady=(8, 0))
        ttk.Button(buttons, text='Cancel', command=dialog.destroy).pack(side='left', padx=4)
        ttk.Button(buttons, text='Save', command=save).pack(side='left')

    def drag_start(self, event):
        self.drag = (event.x_root-self.root.winfo_x(), event.y_root-self.root.winfo_y())

    def drag_move(self, event):
        self.root.geometry(f'+{max(0, event.x_root-self.drag[0])}+{max(0, event.y_root-self.drag[1])}')

    def drag_end(self, event):
        self.persist(replace(self.settings, x=self.root.winfo_x(), y=self.root.winfo_y()))

    def handle(self, command, value):
        actions = {'visibility': self.toggle_visibility, 'import_model': self.import_model,
                   'import_skin': self.import_skin, 'export_model': self.export_template, 'settings': self.open_settings,
                   'pause': self.toggle_pause, 'feed': self.feed, 'quit': self.quit}
        if command == 'model':
            self.select_model(value)
        else:
            actions[command]()

    def frame(self):
        if self.closed:
            return
        try:
            while True:
                command, value = self.commands.get_nowait()
                self.handle(command, value)
                if self.closed:
                    return
        except Empty:
            pass
        now = time.monotonic()
        dt, self.previous = now-self.previous, now
        try:
            presses = self.counter.poll() if self.counter else 0
        except RuntimeError as error:
            messagebox.showerror('WheekKeys', str(error), parent=self.root)
            self.quit()
            return
        pet = self.scene.advance(dt, 0 if self.settings.paused else presses)
        self.configure_pet()  # --demo creates a fresh pet at each loop boundary.
        if not self.hidden:
            image = render(pet, self.skin, self.transparent, self.model)
            if self.settings.scale != 1:
                image = image.resize((round(640*self.settings.scale), round(224*self.settings.scale)), Image.Resampling.NEAREST)
            self.label.image = ImageTk.PhotoImage(image)
            self.label.configure(image=self.label.image)
        self.root.after(16, self.frame)

    def quit(self):
        if self.closed:
            return
        self.closed = True
        if self.tray:
            self.tray.stop()
        if self.counter:
            self.counter.close()
        self.root.destroy()


def main():
    parser = argparse.ArgumentParser(description='Type to grow hay for your guinea pig.')
    parser.add_argument('--skin', help='Palette JSON override for this session')
    parser.add_argument('--demo', action='store_true', help='Automatic ten-second loop; no global keyboard input')
    args = parser.parse_args()
    if sys.platform != 'win32' and not args.demo:
        parser.error('Global keyboard mode requires Windows. Use --demo for an animation preview.')
    root = tk.Tk()
    try:
        Application(root, args)
        root.mainloop()
    except Exception as error:
        messagebox.showerror('WheekKeys could not start', str(error))
        raise


if __name__ == '__main__':
    main()
