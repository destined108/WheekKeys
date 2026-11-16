# 画出你家的豚鼠

复制 `template.json` 为 `my-cavy.json`，保留字段，把颜色改成 `#RRGGBB`：

| 字段 | 部位 |
| --- | --- |
| name | 花色名称（不影响动画） |
| fur | 身体底色 |
| patch | 背部斑块和耳朵外侧 |
| cream | 脸部和脚 |
| ear | 耳朵内侧、鼻子和脚掌 |
| eye | 眼睛与嘴 |

在仓库根目录运行 `python -m wheekkeys --demo --skin skins/my-cavy.json` 预览。下载版可运行 `WheekKeys.exe --skin C:\path\my-cavy.json`；外部 JSON 不需要重新打包。

提交时添加一个 JSON 和预览图，并说明花色名称。请仅提交有权分享的素材，不放入私人信息。当前原型的素材包支持配色替换，身体轮廓来自 `assets/guinea-pig.png` 的四格精灵图（清醒、跑动、嚼草、趴睡），跑步使用 `assets/guinea-pig-walk.png` 的独立四帧步态，动画由共享渲染器提供。默认花色保留原画；修改颜色后按毛色区域映射，并保留明暗层次。
