# WheekKeys — 豚鼠桌宠

**敲键盘长牧草，豚鼠跑来吃。**

[English](README.md) · 简体中文

![打字长草，土豆跑来吃草，再回去趴下](docs/demo-typing-v3.gif)

[![Windows 下载构建](https://img.shields.io/badge/Windows-下载构建-78ad63?logo=windows&logoColor=white)](https://github.com/destined108/WheekKeys/actions/workflows/windows.yml)
[花色模板](skins/template.json) · [做一只你家的豚鼠](skins/README.md)

> 早期原型，尚未发布安装包或 Release。按钮前往 Windows 构建页：选择成功的运行，在 **Artifacts → WheekKeys-Windows** 下载 ZIP，解压运行 `WheekKeys.exe`。下载需要登录 GitHub，可执行文件尚未签名。请下载最新提交对应的构建，以获得修正后的打字检测。

## 十秒就懂

打开程序，留在屏幕角落，切到记事本或其他应用正常打字。每次新按下一个键，牧草增加一根，草下方的小按键会亮一下。十二格进度填满，土豆就跑来嚼草，再回去趴下。长按只算一次。

- Windows 10/11：透明置顶小窗，默认右下角。
- 左键拖动；右键手动喂草或退出；窗口有焦点时按 Esc 退出。
- 没有账号、积分或联网服务。
- `--demo` 是自动十秒演示，**不会响应真实打字**；真实互动请不带该参数启动。

GIF 和程序的 `--demo` 共用固定步长时间线、十二次模拟按键、绘图和按键反馈。GIF 是渲染预览，并非 Windows 桌面录屏；真实模式按你的打字速度长草。

## 键盘隐私

Windows 版通过带消息循环的键盘钩子累计新按下的次数，能够接收动画帧之间的快速轻触。不将按键转换成文字，不读取窗口标题或剪贴板，不保存、上传键盘事件。只在内存中保留待消费的次数和当前按住的键标识，用于过滤长按重复；松开即移除。修饰键和鼠标不计入。输入正常传递，退出时移除钩子，通常无需管理员权限。Windows 安全桌面不在检测范围内。

## 从源码运行

安装 Python 3.12（包含 Tk），在仓库根目录执行：

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m wheekkeys
```

自动预览，不读取全局键盘（Linux/macOS 需有图形显示环境）：

```powershell
.venv\Scripts\python -m wheekkeys --demo
```

使用自定义花色：

```powershell
.venv\Scripts\python -m wheekkeys --skin skins\template.json
```

## 开发与打包

```sh
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m docs.make_demo
```

在 Windows 打包：

```powershell
python -m pip install pyinstaller==6.16.0
python -m PyInstaller --noconfirm --clean --onefile --windowed --name WheekKeys --add-data "skins;skins" --add-data "assets;assets" launcher.py
```

输出为 `dist/WheekKeys.exe`。CI 测试并保存构建产物，不自动发布 Release。

Windows 人工验收：不带 `--demo` 启动，切到记事本快速敲十二次，确认按键反馈、十二格进度和完整吃草循环；长按只算一次。再检查拖动、退出、演示模式及自定义花色。自动测试覆盖计数、反馈、时间线、动画和换色；原生 Windows 桌面与钩子仍需实机验证。

## 把你家的豚鼠带来

复制[模板](skins/template.json)，改五个颜色即可。欢迎附预览图提交花色 PR，或在 Issue 分享。详见[花色指南](skins/README.md)。如果土豆让你笑了一下，欢迎给个 Star，或者把十秒演示分享给喜欢豚鼠的人。

MIT License。角色精灵图根据视觉参考使用 AI 辅助生成，项目内素材随仓库以 MIT 许可提供。
