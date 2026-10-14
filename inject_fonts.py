# -*- coding: utf-8 -*-
"""步骤② 字体注入: 4 个 UI 字体 -> fusion12; Symbola -> 原版 TTF + 动态渲染
输入 common.ASSETS_NEW (纯文本版) 输出 common.ASSETS_FINAL"""
import UnityPy, sys, os
sys.stdout.reconfigure(encoding="utf-8")
import common

fusion = open(common.FUSION_TTF, "rb").read()
symbola = open(common.SYMBOLA_TTF, "rb").read()

env = UnityPy.load(common.ASSETS_NEW)
for o in env.objects:
    if o.type.name != "Font":
        continue
    d = o.read()
    d.m_FontRenderingMode = 2
    if d.m_Name == "Symbola":
        d.m_FontData = symbola
        src = "symbola(原版)"
    else:
        d.m_FontData = fusion
        src = "fusion12-zh_hans"
    d.m_CharacterRects = []
    d.save()
    print(f"  {d.m_Name} -> {src}")

saved = env.file.save()
with open(common.ASSETS_FINAL, "wb") as f:
    f.write(saved)
print("saved:", common.ASSETS_FINAL, f"{os.path.getsize(common.ASSETS_FINAL):,} bytes")
