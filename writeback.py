# -*- coding: utf-8 -*-
"""步骤① 写回器: 直读 translate/byfile/*.tsv (ID/Col/CellKey/English/Chinese)
-> 修改 Text136 文本 -> UnityPy 写回 resources.assets
输出: common.TEXT_OUT/*.txt + common.ASSETS_NEW
"""
import io, os, re, sys, collections
sys.stdout.reconfigure(encoding="utf-8")
import common

LF_FILES = {"Dialogue_Isles.txt", "HallowNPC_Test.txt", "HallowQ.txt", "credits_Eng.txt",
            "delusionAlchemyComboData_Master.txt", "delusionItemData_Master.txt",
            "delusionPlayerHouse_Upgrades.txt", "Test_Dialogue.txt", "Test_Thief.txt",
            "Test_Witch.txt", "unTest_Bartender.txt", "unTest_Noble.txt", "unTest_Shady.txt",
            "unTest_Shopkeep.txt", "unTest_Sleeping.txt", "unTest_Slouch.txt", "unTest_View.txt"}
NO_TOUCH = {"LineBreaking Following Characters.txt", "LineBreaking Leading Characters.txt",
            "Resources File Explanation.txt", "credits_Eng.txt",
            "DebugDialogue.txt", "Test_Dialogue.txt", "Test_Thief.txt", "Test_Witch.txt",
            "unTest_Bartender.txt", "unTest_Noble.txt", "unTest_Shady.txt",
            "unTest_Shopkeep.txt", "unTest_Sleeping.txt", "unTest_Slouch.txt", "unTest_View.txt"}

CELL_SPLIT = re.compile(r'\|(?=(?:[^"]*"[^"]*")*[^"]*$)')

def repair_mixed(raw):
    out, i, n = [], 0, len(raw)
    while i < n:
        b = raw[i]
        if b < 0x80:
            out.append(chr(b)); i += 1; continue
        matched = False
        for l in (2, 3, 4):
            if i + l <= n:
                try:
                    out.append(raw[i:i+l].decode("utf-8")); i += l; matched = True; break
                except UnicodeDecodeError:
                    pass
        if not matched:
            out.append(raw[i:i+1].decode("cp1252")); i += 1
    return "".join(out)

def load_lines(fn):
    raw = open(os.path.join(common.TEXT_IN, fn), "rb").read()
    try:
        txt = raw.decode("utf-8")
    except UnicodeDecodeError:
        txt = repair_mixed(raw)
    sep = "\r\n" if fn not in LF_FILES else "\n"
    return txt.split(sep), sep

def rowid_to_row(dn):
    """Text136 文件: 物理行号 -> 行ID (重复 ID 加 #序号, 与 make_byfile 一致)"""
    lines, _ = load_lines(dn + ".txt")
    ids, seen = {}, {}
    for li, line in enumerate(lines):
        if not line.strip() or "|" not in line:
            continue
        c0 = CELL_SPLIT.split(line)[0].strip()
        if not c0:
            continue
        k = seen.get(c0, 0)
        ids[li] = c0 if k == 0 else f"{c0}#{k}"
        seen[c0] = k + 1
    return ids

def wrap_like(orig, zh):
    if len(orig) >= 2 and orig[0] == '"' and orig[-1] == '"':
        if len(zh) >= 2 and zh[0] == '"' and zh[-1] == '"':
            return zh
        return '"' + zh + '"'
    return zh

# ---------- 1. 读 byfile, 构建映射 ----------
by_file = collections.defaultdict(list)
n_trans = 0
for fn in sorted(os.listdir(common.BYFILE)):
    if not fn.endswith(".tsv"):
        continue
    dn = fn[:-4]
    ids = None
    for l in io.open(os.path.join(common.BYFILE, fn), encoding="utf-8").read().split("\n")[1:]:
        if not l:
            continue
        p = l.split("\t")
        if len(p) != 5:
            continue
        rid, col, zh = p[0], int(p[1]), p[4]
        if not zh:
            continue
        if ids is None:
            ids = rowid_to_row(dn)
        row = None
        for li, v in ids.items():
            if v == rid:
                row = li
                break
        if row is None:
            print(f"!! 找不到行: {dn} {rid}")
            continue
        by_file[dn].append((row, col, zh))
        n_trans += 1
print(f"翻译映射: {n_trans} 条, 文件数 {len(by_file)}")

# ---------- 2. 文本替换 ----------
os.makedirs(common.TEXT_OUT, exist_ok=True)
total = 0
for dn, items in sorted(by_file.items()):
    fn = dn + ".txt"
    lines, sep = load_lines(fn)
    n = 0
    for row, col, zh in items:
        before = lines[row].count('"')
        cells = CELL_SPLIT.split(lines[row])
        cells[col] = wrap_like(cells[col], zh)
        lines[row] = "|".join(cells)
        if lines[row].count('"') % 2 != before % 2:
            print(f"!! 引号奇偶破坏 {fn} L{row}")
            sys.exit(1)
        n += 1
    with open(os.path.join(common.TEXT_OUT, fn), "wb") as f:
        f.write(sep.join(lines).encode("utf-8"))
    total += n
print(f"文本替换完成: {total} cell")

en_out = os.path.join(common.TEXT_OUT, "delusionItemText_English.txt")
base = open(en_out, "rb").read()
for lang in ("French", "German", "Spanish"):
    with open(os.path.join(common.TEXT_OUT, f"delusionItemText_{lang}.txt"), "wb") as f:
        f.write(base)
print("法/德/西 已复制英文产物")

# ---------- 3. UnityPy 写回 ----------
import UnityPy
env = UnityPy.load(common.GAME_ASSETS)
replaced = 0
for obj in env.objects:
    if obj.type.name != "TextAsset":
        continue
    d = obj.read()
    new_path = os.path.join(common.TEXT_OUT, d.m_Name + ".txt")
    if not os.path.exists(new_path):
        continue
    data = open(new_path, "rb").read()
    d.m_Script = data.decode("utf-8")
    d.save()
    replaced += 1
print(f"TextAsset 替换: {replaced} 个")
saved = env.file.save()
with open(common.ASSETS_NEW, "wb") as f:
    f.write(saved)
print("已保存:", common.ASSETS_NEW, f"{os.path.getsize(common.ASSETS_NEW):,} bytes")
