---
name: create-guinea-pig
description: Create or update WheekKeys guinea pig coat colors or complete models from reference photos or a description, validate and preview the result, and deliver importable resources.
---

# Create a WheekKeys guinea pig

Turn the user's guinea pig reference into an importable palette or complete character. Reply in the user's language. Inspect `wheekkeys/art.py`, `skins/template.json`, and the target resources before working. For full models also read `models/README.md` or `models/README.zh-CN.md` and inspect `wheekkeys/models.py`. Use the existing checkout; do not create a worktree. Run commands from the WheekKeys repository root using its configured Python environment.

## Understand the character

Use the user's photos, name and requested style. Infer coat regions, body proportions, eyes and ears from the reference. If no photo was supplied, work from their description or ask for a reference only if needed. Ask for missing essentials without blocking independent work. Do not invent a pet's identifying markings. Offer palette-only changes when those satisfy the request; explain that a full model replaces the shape and all animation artwork.

For a new model choose a unique lowercase, hyphenated slug and use `models/community/<slug>/`. For edits use the explicitly requested existing pack; inspect and preserve unrelated files and user changes. Do not overwrite an existing pack with a starter template. Do not replace the bundled Potato artwork or change application code merely to install a model.

## Create or update coat colors

Take this branch for a colors-only request. Keep the current shape and animation artwork; no image generation is necessary. For a new palette, use `skins/community/<slug>/skin.json`; for edits preserve the user's source and unrelated files. Copy `skins/template.json` as the starting schema, or use the target model's existing `skin.json`.

Keep all field names. Set a display name and exactly formatted `#RRGGBB` color values:

| Field | Typical region |
| --- | --- |
| `name` | Palette display name, does not affect animation |
| `fur` | Main fur color |
| `patch` | Dark fur patches and outer ears |
| `cream` | Light face and foot fur |
| `ear` | Pink areas, including inner ears, nose and paws |
| `eye` | Dark details, including eyes and mouth |

Regions are inferred from the original image's hue and brightness, not independent painted layers. Colors can affect more than one anatomical region. Preserve shading, inspect all poses, and explain when a requested marking needs new artwork rather than recoloring. The default five values preserve the original image.

From the repository root, generate a validated ten-second preview with the bundled model:

```sh
python .agents/skills/create-guinea-pig/scripts/model_pack.py preview-skin skins/community/my-cavy/skin.json --output skins/community/my-cavy/preview.gif
```

For a supplied custom model append `--model <folder-containing-model.json>`; otherwise the preview uses Potato. Inspect the rendered result and refine the colors. If a desktop is available, also run `python -m wheekkeys --demo --skin skins/community/my-cavy/skin.json` to inspect the default-model preview. Report which model was used for preview; do not imply that recoloring creates a new body or coat pattern.

Deliver the exact `skin.json` and preview paths. Tell the user to right-click the pet or tray icon → **Import colors… / 导入花色… / 匯入花色…** and choose the JSON file. The app copies it into `%APPDATA%\WheekKeys\skins`, applies it, and remembers it. Switching models restores that model's own palette; import the palette again to apply it to the new model. The `--skin` CLI option applies a palette only for that session. No executable rebuild, model ZIP, or manual AppData edits are needed.

For sharing include the palette, its name and preview, without personal reference photos. Stop here for palette-only work. Continue below only when the user needs a full model.

## Prepare a self-contained model pack

The helper lives beside this skill at `scripts/model_pack.py`. In the repository it is `.agents/skills/create-guinea-pig/scripts/model_pack.py`. If the skill is installed elsewhere, use the actual script path. Run it from the repository root.

Create a starter only for a new destination:

```sh
python .agents/skills/create-guinea-pig/scripts/model_pack.py init models/community/my-cavy --name "My Cavy"
```

This copies Potato as a layout template. It is NOT the finished custom character. Replace the artwork with the user's character before claiming a new model is complete.

Required files:

```text
models/community/<slug>/
  model.json       # name and relative paths to poses, walk, skin
  poses.png        # four equal-width cells: awake, walking fallback, chewing, sleeping
  walk.png         # four equal-width cells: one complete right-facing walk cycle
  skin.json        # name plus fur, patch, cream, ear, eye as #RRGGBB
  preview.gif      # generated from the actual renderer
  README.md        # character name, attribution/license, how to import
```

Use relative paths that stay inside the pack. Never include scripts, executable files, personal photos, keyboard data or local preferences in the deliverable. The original photo is a reference, not a public resource: do not add it to Git or a ZIP unless the user explicitly asks and can share it. Document the source and usage rights of the artwork; do not assert a license for somebody else's files. Project-created artwork follows the repository license when appropriate.

## Make consistent artwork

Use available image-generation or image-editing tools when drawing is requested. Inspect existing images first. If no image tools are available, use supplied sprite art or explain the specific missing capability; do not call a renamed Potato template a finished new pet.

Both sheets must be PNG with actual transparency, four equal columns and a visible full animal in every cell; maximum size 8192×4096. Face RIGHT. Leave transparent margins so whiskers and paws do not get cut off. No background, captions, grass, keyboard or props in the sprites.

Keep the same character, scale, coat markings, face angle and ground line across a sheet and compatible body proportions across both sheets. The app scales each sheet into an 86×62 scene-pixel canvas. Inspect at the actual on-screen size, not just full resolution.

For `walk.png`, draw four distinct phases: reach, pass, opposite reach, opposite pass. Animate short alternating feet under a low, grounded body. Keep the torso steady. Do not simulate walking with a single standing pose, rotation, floating, or a whole-body bounce. Check that the last phase loops cleanly into the first. Chewing should bring the mouth to the grass; sleeping should be a tucked, closed-eye loaf.

Keep the default five palette values from `skins/template.json` when the original painted colors should be preserved. Non-default colors trigger the renderer's region-based recoloring; test the result before using them. Set the display name in both JSON files without changing field names.

## Validate and preview

```sh
python .agents/skills/create-guinea-pig/scripts/model_pack.py check models/community/my-cavy
python .agents/skills/create-guinea-pig/scripts/model_pack.py preview models/community/my-cavy
python .agents/skills/create-guinea-pig/scripts/model_pack.py package models/community/my-cavy --output dist/my-cavy.zip
```

The helper calls the application's real loader, requires transparency and all eight visible frames, exports a ten-second preview using the shared scene and renderer, and packages only the model's declared files plus README/license/preview if present. It does not modify user settings or install the model.

Inspect `preview.gif` and individual poses/cycle at normal size. Correct inconsistent anatomy, missing markings, clipping, foot sliding, size changes, or a misplaced mouth. Run relevant existing tests when code was changed. Structural checks do not prove the animation looks right. If Windows is unavailable, explicitly distinguish renderer validation from unperformed Windows import/desktop checks. Recheck the pack after the last resource edit.

## Deliver and explain installation

For a full model, provide the exact pack folder, preview, ZIP and validation results in the user's language. Explain:

1. Unzip the ZIP if needed.
2. Right-click the pet or tray icon → **Import model… / 导入模型… / 匯入模型…**.
3. Choose the folder containing `model.json`, not the ZIP or just a PNG.
4. The app copies the files into `%APPDATA%\WheekKeys\models\model-<id>`, selects the model, and remembers it. Users need not manually edit that directory, overwrite `assets/`, rebuild the exe, or restart the application.
5. It can be selected again under **Pet model / 宠物模型 / 寵物模型**. Switching models restores that model's palette.

Offer a screenshot or GIF for sharing. Do not commit, push, publish or upload the pack unless requested. Model creation does not imply permission to share personal reference photos.
