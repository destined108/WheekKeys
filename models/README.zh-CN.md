# 制作你自己的豚鼠模型

[English](README.md) · 简体中文 · [返回项目首页](../README.zh-CN.md)

模型包可以替换角色的外形和整套动作。如果只是想换成自家豚鼠的毛色，先看[花色制作指南](../skins/README.zh-CN.md)就够了。

可在宠物右键或托盘菜单的 **语言** 中选择简体中文、繁體中文、English，或跟随系统。下文同时列出简体中文和英文菜单名称，方便对照。

## 让 agent 帮你制作

在编程 agent 中打开这个仓库，附上豚鼠照片或描述，再发送下面这段话。完整流程已整理为 [create-guinea-pig skill](../.agents/skills/create-guinea-pig/SKILL.md)。

> 请读取 `.agents/skills/create-guinea-pig/SKILL.md` 并按照说明，为附件里的豚鼠制作模型。名字是：____。将资源放到 `models/community/<模型名>/`，生成预览、检查模型，并给我可导入的 ZIP 和使用步骤。不要把我的参考照片放进模型包。

Codex 等支持发现仓库 skill 的 agent 可以直接调用 `$create-guinea-pig`。如果你的 agent 不支持 skill，就把 `SKILL.md` 的内容和上面这段话一起发给它。agent 需要能访问本仓库和 Python 依赖；绘制新角色还需要图像工具，或由你提供动作图。没有图像工具时，它可以准备模板、检查已有资源，但不能把复制的模板当作你的新模型。

### 资源放在哪里

- **仓库里：** 每个模型单独放在 `models/community/<模型名>/`，包含 `model.json`、`poses.png`、`walk.png`、`skin.json`。分享时再附 `preview.gif` 和说明素材来源、许可的 README。具体结构见[资源目录说明](community/README.md)。
- **交付时：** 让 agent 打包成 `dist/<模型名>.zip`。`dist/` 已被 Git 忽略，制作模型的原始资源保留在模型文件夹中。可以把 ZIP 发给其他用户，或提交包含模型源文件的 PR。
- **程序里：** 解压 ZIP，在菜单选择 **导入模型…**，选中包含 `model.json` 的文件夹。程序会复制到 `%APPDATA%\WheekKeys\models\model-<id>`。不用把资源塞进 exe 旁边，也不要覆盖 `assets/`；仓库中的模型不会自动安装。

skill 附带辅助工具，agent 可以在项目根目录执行：

```sh
python .agents/skills/create-guinea-pig/scripts/model_pack.py init models/community/my-cavy --name "My Cavy"
python .agents/skills/create-guinea-pig/scripts/model_pack.py check models/community/my-cavy
python .agents/skills/create-guinea-pig/scripts/model_pack.py preview models/community/my-cavy
python .agents/skills/create-guinea-pig/scripts/model_pack.py package models/community/my-cavy --output dist/my-cavy.zip
```

`init` 只复制内置模型作为布局模板。替换为你家豚鼠的动作图后，再检查、生成预览并打包。下面也保留了手动制作的步骤。

## 1. 导出一份模板

右键点击宠物或 Windows 托盘图标，选择 **导出模型模板…（Export model template…）**，再选择保存位置。程序会新建一个文件夹，放入当前模型的图片和配置，不会覆盖已有文件夹。

目前内置的模型是「土豆」。你可以以它为模板，修改图片，再到 `model.json` 中填写自己的角色名称：

```json
{
  "name": "My guinea pig",
  "poses": "poses.png",
  "walk": "walk.png",
  "skin": "skin.json"
}
```

这四个文件需要一起保存在模型文件夹中。文件名可以修改，但 `model.json` 中填写的路径必须与实际文件一致。

## 2. 绘制动作图片

| 文件 | 从左到右的排列方式 |
| --- | --- |
| `poses.png` | 四个等宽区域，依次为清醒、备用行走姿势、嚼草、趴下睡觉 |
| `walk.png` | 四个等宽区域，组成一套完整的行走循环，角色朝右 |
| `skin.json` | 与[花色模板](../skins/template.json)相同的五个颜色字段和名称 |

两张动作图都使用透明背景的 PNG，每个区域放一只完整、可见的角色。不同帧之间应保持体型、大小和脚底高度一致，避免走动时忽大忽小、身体晃动或脚底打滑。可以直接参考导出的图片安排布局。

每张图片最大为 **8192×4096 像素**，宽度必须能被四整除。程序会把角色缩放到 **86×62 个场景像素**的画布内，同一张图片中的所有帧使用相同缩放比例。默认配色保留原画；自定义花色会根据图片颜色识别区域，换色时保留明暗层次，详见[花色制作指南](../skins/README.zh-CN.md)。

`model.json` 中的路径只能指向模型文件夹内部的文件。模型包只包含图片和 JSON 配置，程序不会从中加载 Python 脚本、插件或可执行程序。

## 3. 导入并试用

右键点击宠物或托盘图标，选择 **导入模型…（Import model…）**，再选中包含 `model.json` 的文件夹。程序会检查文件，把所需内容复制到用户目录，并立即切换到新模型。导入成功后，原来的素材文件夹可以移走或删除。

安装好的模型会出现在两处菜单的 **宠物模型（Pet model）** 中，下次启动时也会保留你的选择。切换模型会恢复该模型自带的花色。

试用时，看看它是否面朝牧草，走路时大小是否稳定，嚼草的位置是否对得上，以及吃完后能否回去趴下。也建议检查实际打字、手动喂草、不同显示大小和重启后的效果。

## 4. 分享完整模型包

分享时，请把模型文件夹中的四个文件一起附上，并提供角色名称和截图或 GIF。你可以在 Issue 中分享，也可以提交 PR。请只使用你有权公开分享的素材，不要包含个人隐私信息。

Windows 上的设置保存在 `%APPDATA%\WheekKeys\settings.json`，模型放在同级的 `models` 文件夹，导入的花色放在 `skins` 文件夹。制作或更换宠物不需要修改、重新打包 exe。
