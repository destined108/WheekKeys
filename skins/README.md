# Make your own guinea pig colors

English · [简体中文](README.zh-CN.md) · [Back to WheekKeys](../README.md)

A palette changes your pet's colors while keeping its shape and animations. To draw an entirely new character, follow the [model pack guide](../models/README.md).

Choose **Language** in either menu to use Simplified Chinese, Traditional Chinese, English, or follow your system language. The steps below use the English labels.

## 1. Copy the template

Copy [template.json](template.json) to `my-cavy.json`. Keep all field names and replace the colors with hex values in `#RRGGBB` format:

| Field | Purpose |
| --- | --- |
| `name` | Palette name; does not affect animations |
| `fur` | Main fur color |
| `patch` | Dark fur patches and outer ears |
| `cream` | Light fur on the face and feet |
| `ear` | Pink areas such as inner ears, nose, and paws |
| `eye` | Dark details such as eyes and mouth |

Color regions are detected from the artwork, so these are approximate areas rather than individual paint layers. Shading is preserved when colors are replaced. The default palette leaves the original artwork unchanged.

## 2. Try it on your pet

Right-click the pet or the Windows tray icon, choose **Import colors…**, and select your JSON file. The app copies it into your user data folder and remembers it for the next launch. Switching models restores the selected model's own colors; import your palette again to apply it to that model.

You can also preview a palette from the repository root:

```sh
python -m wheekkeys --demo --skin skins/my-cavy.json
```

Or launch the downloaded Windows app with a palette for that session:

```powershell
.\WheekKeys.exe --skin "C:\path\my-cavy.json"
```

No repackaging is needed. `--demo` plays an automatic animation; omit it to try real typing on Windows. With source commands, use the Python interpreter from your configured virtual environment.

## 3. Share your cavy

Share a screenshot or GIF in an Issue, or submit a PR with your palette JSON, its name, and a preview. Only share artwork you have permission to distribute, and keep personal information out of the files.

Want to change the body shape or draw your own walking and eating animations? Continue with [pet model packs](../models/README.md).
