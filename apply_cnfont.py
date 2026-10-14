# -*- coding: utf-8 -*-
"""步骤③ 三件套替换（最终版流程）
- TMP 1255: raw 拼接（game 头 + bundle body，PPtr 字节重映射）
- Atlas 28: bundle 图集（翻转行序后写入）
- Material 2: 原版材质(51参数, shader 30) + 仅改 _TextureWidth/_TextureHeight=2048（日包模式）
注意: 游戏更新后需核对三个 path_id (脚本顶部常量) 与 TMP 结构是否变化
"""
import UnityPy, sys, struct, os
from PIL import Image
sys.stdout.reconfigure(encoding="utf-8")
import common

BASE   = common.ASSETS_FINAL      # 字体注入后的基线
ORIGIN = common.ASSETS_NEW        # 纯文本版 (Material/TMP 头均为原版状态)
BUNDLE = common.BUNDLE
OUT    = common.ASSETS_FINAL
GAME_TMP_PID, GAME_ATLAS_PID, GAME_MAT_PID = 1255, 28, 2

# ---------- bundle 侧 ----------
benv = UnityPy.load(BUNDLE)
b_font_obj = b_atlas_obj = None
for o in benv.objects:
    if o.type.name == "MonoBehaviour": b_font_obj = o
    elif o.type.name == "Texture2D": b_atlas_obj = o

font_raw = bytearray(b_font_obj.get_raw_data())
nlen = struct.unpack("<i", font_raw[0x1C:0x20])[0]
name_end = 0x20 + nlen
body_start = (name_end + 3) & ~3
b_body = bytes(font_raw[body_start:])
print("bundle font body:", len(b_body), "bytes")

B_MAT_PID = [o.path_id for o in benv.objects if o.type.name == "Material"][0]
B_ATLAS_PID = b_atlas_obj.path_id
n_sub = 0
for old, new in ((struct.pack("<q", B_MAT_PID), struct.pack("<q", GAME_MAT_PID)),
                 (struct.pack("<q", B_ATLAS_PID), struct.pack("<q", GAME_ATLAS_PID))):
    c = b_body.count(old)
    b_body = b_body.replace(old, new)
    n_sub += c
assert n_sub >= 2, "PPtr 替换次数异常"
print("PPtr remapped x", n_sub)

img = b_atlas_obj.read().image
if img.mode == "RGBA":
    img = img.getchannel("A")
img = img.transpose(Image.FLIP_TOP_BOTTOM)   # Unity 纹理 bottom-up
atlas_bytes = img.tobytes()

# 原版材质 (shader 30, 51 参数) — 从纯文本版 ORIGIN 取 (Material 未被文本写回改动)
orig_env = UnityPy.load(ORIGIN)
orig_mat_tt = None
for o in orig_env.objects:
    if o.type.name == "Material" and o.path_id == GAME_MAT_PID:
        orig_mat_tt = o.read_typetree()
new_floats = []
for first, second in orig_mat_tt["m_SavedProperties"]["m_Floats"]:
    if first in ("_TextureWidth", "_TextureHeight"):
        print(" ", first, second, "-> 2048")
        new_floats.append((first, 2048.0))
    else:
        new_floats.append((first, second))
orig_mat_tt["m_SavedProperties"]["m_Floats"] = new_floats

# ---------- 写入基线 ----------
env = UnityPy.load(BASE)
done = set()
for o in env.objects:
    pid = o.path_id
    if pid == GAME_ATLAS_PID and o.type.name == "Texture2D":
        tt = o.read_typetree()
        tt["m_Width"] = img.width
        tt["m_Height"] = img.height
        tt["m_TextureFormat"] = 1
        tt["m_CompleteImageSize"] = len(atlas_bytes)
        tt["m_ImageCount"] = 1
        tt["image data"] = atlas_bytes
        tt["m_StreamData"] = {"offset": 0, "size": 0, "path": ""}
        o.save_typetree(tt)
        done.add("atlas")
        print("Atlas 28:", img.width, "x", img.height, "Alpha8")
    elif pid == GAME_MAT_PID and o.type.name == "Material":
        o.save_typetree(orig_mat_tt)
        done.add("material")
        print("Material 2: original(51 params, shader 30) + size 2048")
    elif pid == GAME_TMP_PID and o.type.name == "MonoBehaviour":
        game_raw = bytearray(o.get_raw_data())
        g_nlen = struct.unpack("<i", game_raw[0x1C:0x20])[0]
        g_body_start = ((0x20 + g_nlen) + 3) & ~3
        o.set_raw_data(bytes(game_raw[:g_body_start]) + b_body)
        done.add("tmp")
        print("TMP 1255: head", g_body_start, "+ body", len(b_body))

assert done == {"atlas", "material", "tmp"}, done
saved = env.file.save()
with open(OUT, "wb") as f:
    f.write(saved)
print("saved:", OUT, f"{os.path.getsize(OUT):,}")
