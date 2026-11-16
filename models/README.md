# Make your own guinea pig model

English · [简体中文](README.zh-CN.md) · [Back to WheekKeys](../README.md)

A model pack replaces the character's artwork and animation frames. If you only want to change colors, ask your agent to use the palette workflow in [the same skill](../.agents/skills/create-guinea-pig/SKILL.md#create-or-update-coat-colors).

Choose **Language** in either menu to use Simplified Chinese, Traditional Chinese, English, or follow your system language. The steps below use the English labels.

## Let an agent make your cavy

Open this repository in your coding agent, attach a photo or describe your guinea pig, and send the prompt below. The workflow is saved as [the create-guinea-pig skill](../.agents/skills/create-guinea-pig/SKILL.md).

> Read `.agents/skills/create-guinea-pig/SKILL.md` and follow it to create a model of my guinea pig from the attached reference. Name: ____. Save the pack to `models/community/<slug>/`, generate a preview, validate it, and give me an importable ZIP plus installation steps. Do not include my reference photos in the pack.

Codex and agents that discover repository skills can invoke `$create-guinea-pig`. If your agent does not support skills, send it the contents of `SKILL.md` with the prompt. The agent needs this checkout and Python dependencies; making new artwork also requires an image tool or your supplied sprites. Without an image tool, it can prepare the layout and check supplied files, but should not call a copied template a new model.

### Where to put the resources

- **In the repository:** `models/community/<slug>/` contains `model.json`, `poses.png`, `walk.png`, and `skin.json`. Add `preview.gif` and a README with attribution/license for sharing. See the [folder layout](community/README.md).
- **For delivery:** ask the agent to create `dist/<slug>.zip`. `dist/` is ignored by Git; source artwork remains in the model folder. Send the ZIP to users, or include the source pack in a PR.
- **In the application:** unzip, choose **Import model…**, and select the folder containing `model.json`. The app copies the files to `%APPDATA%\WheekKeys\models\model-<id>`. Do not put model files beside the exe or overwrite `assets/`; repository packs are not automatically installed.

The skill includes a helper for the agent to run from the repository root:

```sh
python .agents/skills/create-guinea-pig/scripts/model_pack.py init models/community/my-cavy --name "My Cavy"
python .agents/skills/create-guinea-pig/scripts/model_pack.py check models/community/my-cavy
python .agents/skills/create-guinea-pig/scripts/model_pack.py preview models/community/my-cavy
python .agents/skills/create-guinea-pig/scripts/model_pack.py package models/community/my-cavy --output dist/my-cavy.zip
```

`init` copies the current built-in artwork as a starting template. Replace that artwork before the final check, preview and package steps. The following sections describe manual authoring.

## 1. Export a starting template

Right-click the pet or the Windows tray icon and choose **Export model template…**. Select a destination; the app creates a new folder containing the current model's artwork and configuration without overwriting existing folders.

The app includes **Potato** and **Mochi** as built-in models. Select either from **Pet model**, then export it as a starting point, then edit the images and the name in `model.json`:

```json
{
  "name": "My guinea pig",
  "poses": "poses.png",
  "walk": "walk.png",
  "skin": "skin.json"
}
```

Keep these four files together in the model folder. The filenames can differ if the manifest points to them correctly.

## 2. Draw the animation frames

| File | Layout, from left to right |
| --- | --- |
| `poses.png` | Four equal-width columns: awake, walking fallback, chewing, sleeping |
| `walk.png` | Four equal-width columns forming a complete walk cycle, facing right |
| `skin.json` | The five-color palette schema from [the template](../skins/template.json), plus its name |

Use transparent PNGs for both sprite sheets, with one complete, visible character inside each column. Keep the body proportions, size, and ground line consistent across frames so the pet does not wobble or slide. Use the exported images as a layout reference.

Each sheet must be at most **8192×4096 pixels**, with width divisible by four. The renderer fits the character into an **86×62 scene-pixel** canvas, using one scale for all frames within each sheet. The default palette preserves the original artwork; custom palettes recolor detected regions while preserving shading. The [skill’s palette workflow](../.agents/skills/create-guinea-pig/SKILL.md#create-or-update-coat-colors) covers color fields and import steps.

All paths in `model.json` must point to files inside the model folder. Model packs contain artwork and JSON only; the app does not load Python scripts, plugins, or executables from them.

## 3. Import and test your model

Right-click the pet or the tray icon, choose **Import model…**, and select the folder containing `model.json`. The app validates the files, copies them into its user data folder, and selects the new model. After import, the original source folder can be removed.

Installed models appear in **Pet model** in both menus. Your selection is remembered after restart. Switching models restores that model's own palette.

Check that your pet faces the food, walks without changing size, chews at the grass, and returns to rest. Also try real typing, manual feeding, different display sizes, and restarting the app.

## 4. Share the complete pack

Share the model folder with all four files, along with a screenshot or GIF and the model's name. You can post it in an Issue or submit a PR. Only include artwork you have permission to distribute, and omit private information.

On Windows, preferences are stored at `%APPDATA%\WheekKeys\settings.json`, model packs under `models`, and imported palettes under `skins`. You do not need to modify or repackage the exe to customize a pet.
