# -*- coding: utf-8 -*-
"""列出 resources.assets 中的 TextAsset 并导出到 Text136/ (写回管线的原文基准)"""
import UnityPy, os, sys
import common

SRC = common.GAME_ASSETS
OUT = common.TEXT_IN
os.makedirs(OUT, exist_ok=True)

env = UnityPy.load(SRC)
text_assets = []
type_counts = {}
for obj in env.objects:
    tn = obj.type.name
    type_counts[tn] = type_counts.get(tn, 0) + 1
    if tn == "TextAsset":
        d = obj.read()
        name = d.m_Name
        script = d.m_Script
        if isinstance(script, str):
            data = script.encode("utf-8", "surrogateescape")
        else:
            data = bytes(script)
        text_assets.append((name, len(data), obj.path_id))
        safe = "".join(c if c.isalnum() or c in "_- ()" else "_" for c in name)
        with open(os.path.join(OUT, f"{safe}.txt"), "wb") as f:
            f.write(data)

print("=== 类型统计 ===")
for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
    print(f"{t:30s} {c}")
print(f"\n=== TextAsset 共 {len(text_assets)} 个 ===")
for name, size, pid in sorted(text_assets):
    print(f"{size:>9,}  {name}")
