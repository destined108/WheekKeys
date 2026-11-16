# Pet model packs

Right-click the pet or the tray icon → **Pet model** to switch installed models. The prototype includes one built-in model, **Potato**. Import your own complete character through **Import model…**. Use **Export model template…** to create a self-contained copy of the current model, then edit its artwork and name.

A pack is a folder with a `model.json` manifest:

```json
{
  "name": "My guinea pig",
  "poses": "poses.png",
  "walk": "walk.png",
  "skin": "skin.json"
}
```

- `poses.png`: four equal-width columns: awake, walking fallback, chewing, sleeping. Transparent PNG.
- `walk.png`: four equal-width columns forming a complete walk cycle, facing right. Transparent PNG. Keep body proportions and foot baseline consistent.
- Each cell must contain a visible sprite. Each sheet must be at most 8192×4096 pixels, with width divisible by four. The renderer fits a character to an 86×62 scene-pixel canvas while retaining a fixed scale across each sheet.
- `skin.json`: the same five-color schema as [the palette template](../skins/template.json). The default palette preserves artwork; palette overrides apply the existing color-region recoloring.
- All manifest paths must stay inside the model folder. No Python code, plugins, or executables are loaded from a model pack.

Import copies the required files into the user's WheekKeys data folder; the original download can then be removed. Imported models appear in both menus and are restored on restart. Export always creates a new folder, preserving existing files. A palette changes colors; a model pack replaces all animation artwork.

On Windows, preferences are stored at `%APPDATA%\WheekKeys\settings.json`, model packs under `models`, and imported palettes under `skins`. Do not edit the bundled application to customize a pet.
