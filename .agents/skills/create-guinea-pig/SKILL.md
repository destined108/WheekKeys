---
name: create-guinea-pig
description: Create or update an importable WheekKeys guinea pig model from reference photos or a description, generate consistent animation artwork, validate it, and deliver a preview and model ZIP.
---

# Create a WheekKeys guinea pig

Turn the user's guinea pig reference into a complete character they can import into WheekKeys. Reply in the user's language. Read `models/README.md` or `models/README.zh-CN.md` and inspect `wheekkeys/models.py`, `wheekkeys/art.py`, and the target model before working. Use the existing checkout; do not create a worktree. Run commands from the WheekKeys repository root using its configured Python environment.

## Understand the character

Use the user's photos, name and requested style. Infer coat regions, body proportions, eyes and ears from the reference. If no photo was supplied, work from their description or ask for a reference only if needed. Ask for missing essentials without blocking independent work. Do not invent a pet's identifying markings. Offer palette-only changes when those satisfy the request; explain that a full model replaces the shape and all animation artwork.

For a new model choose a unique lowercase, hyphenated slug and use `models/community/<slug>/`. For edits use the explicitly requested existing pack; inspect and preserve unrelated files and user changes. Do not overwrite an existing pack with a starter template. Do not replace the bundled Potato artwork or change application code merely to install a model.

## Prepare a self-contained pack

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

Provide the exact pack folder, preview, ZIP and validation results in the user's language. Explain:

1. Unzip the ZIP if needed.
2. Right-click the pet or tray icon → **Import model… / 导入模型… / 匯入模型…**.
3. Choose the folder containing `model.json`, not the ZIP or just a PNG.
4. The app copies the files into `%APPDATA%\WheekKeys\models\model-<id>`, selects the model, and remembers it. Users need not manually edit that directory, overwrite `assets/`, rebuild the exe, or restart the application.
5. It can be selected again under **Pet model / 宠物模型 / 寵物模型**. Switching models restores that model's palette.

Offer a screenshot or GIF for sharing. Do not commit, push, publish or upload the pack unless requested. Model creation does not imply permission to share personal reference photos.
