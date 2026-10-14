# -*- coding: utf-8 -*-
"""恢复 TMP Essentials 到 UnityFontGen/Assets/TextMesh Pro/
原理: TMP 包的 Essential Resources.unitypackage 本质是 tar.gz,
每个 GUID 目录含 asset/asset.meta/pathname, 按 pathname 还原(保留 GUID)。
用法: py restore_tmpeffects.py
前置: Unity 工程至少打开过一次 (Library/PackageCache 里已有 com.unity.textmeshpro)
"""
import os, sys, tarfile, shutil
sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.join(ROOT, "UnityFontGen")
PKG_DIR = os.path.join(PROJ, "Library", "PackageCache")
PKG_NAME = "com.unity.textmeshpro@3.0.6"
OUT_ASSETS = os.path.join(PROJ, "Assets", "TextMesh Pro")

if os.path.exists(OUT_ASSETS):
    print("TextMesh Pro 已存在, 无需恢复")
    sys.exit(0)

pkg = os.path.join(PKG_DIR, PKG_NAME)
pkgfile = os.path.join(pkg, "Package Resources", "TMP Essential Resources.unitypackage")
assert os.path.exists(pkgfile), "找不到 TMP Essential Resources.unitypackage, 请先让 Unity 解析 TMP 包"

tmp = os.path.join(ROOT, "tmp_essentials")
shutil.rmtree(tmp, ignore_errors=True)
with tarfile.open(pkgfile) as tf:
    tf.extractall(tmp)

n = 0
for d in os.listdir(tmp):
    dd = os.path.join(tmp, d)
    if not os.path.isdir(dd) or not os.path.exists(os.path.join(dd, "asset")):
        continue
    pathname = os.path.join(dd, "pathname")
    if not os.path.exists(pathname):
        continue
    rel = open(pathname, encoding="utf-8").read().strip()
    dest = os.path.join(PROJ, rel.replace("Assets/", "", 1))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy(os.path.join(dd, "asset"), dest)
    shutil.copy(os.path.join(dd, "asset.meta"), dest + ".meta")
    n += 1
shutil.rmtree(tmp)
print(f"恢复 TMP Essentials: {n} 项 -> {OUT_ASSETS}")
print("下一步: 用 Unity 打开工程 (或批处理) 让其导入这些资产")
