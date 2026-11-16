# Community model resources / 社区模型资源

Put each complete model in its own folder: `models/community/<slug>/`. For example:

每个完整模型使用一个独立文件夹，例如：

```text
models/community/my-cavy/
  model.json
  poses.png
  walk.png
  skin.json
  preview.gif
  README.md
```

Use a unique lowercase, hyphenated slug. Include the character name, artwork attribution and license in its README. Keep private reference photos out of the pack. ZIP downloads belong in `dist/` (ignored by Git), not in this directory.

文件夹名使用不重复的小写英文，可用连字符分隔。README 写明角色名称、素材来源和许可；不要放入私人参考照片。用于下载的 ZIP 放在 `dist/` 中，该目录不会提交到 Git。

[Agent skill](../../.agents/skills/create-guinea-pig/SKILL.md) · [English guide](../README.md) · [中文指南](../README.zh-CN.md)

Repository folders are for authoring/sharing only. The app does not automatically scan this directory. Import the folder through the pet/tray menu; the app copies it into the per-user model directory.

这里用于制作和分享模型，程序不会自动扫描此目录。请通过宠物或托盘菜单导入模型文件夹，程序会将资源复制到当前用户的模型目录。
