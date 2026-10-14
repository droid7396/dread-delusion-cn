# -*- coding: utf-8 -*-
"""
Dread Delusion 1.3.6 文本提取器
输出: extract/tsv/<file>.tsv + all_texts.tsv + stats.txt + context_notes.txt
TSV 列: DataName  Row  Col  CellKey  English  Chinese
- Row/Col 为文件内原始行列位置(0-based), 写回时按此定位
- CellKey 为可读键(行ID+列名)
"""
import os, re, sys, json
sys.stdout.reconfigure(encoding="utf-8")
import common

SRC = common.TEXT_IN
OUT = os.path.join(common.ROOT, "extract")
TSV_DIR = os.path.join(OUT, "tsv")
os.makedirs(TSV_DIR, exist_ok=True)

# LF 分行的文件(普查结论: crlf=0)
LF_FILES = {"Dialogue_Isles.txt", "HallowNPC_Test.txt", "HallowQ.txt", "credits_Eng.txt",
            "delusionAlchemyComboData_Master.txt", "delusionItemData_Master.txt",
            "delusionPlayerHouse_Upgrades.txt", "Test_Dialogue.txt", "Test_Thief.txt",
            "Test_Witch.txt", "unTest_Bartender.txt", "unTest_Noble.txt", "unTest_Shady.txt",
            "unTest_Shopkeep.txt", "unTest_Sleeping.txt", "unTest_Slouch.txt", "unTest_View.txt"}
# 不翻译的文件
SKIP_FILES = {"LineBreaking Following Characters.txt", "LineBreaking Leading Characters.txt",
              "Resources File Explanation.txt", "credits_Eng.txt",
              "DebugDialogue.txt", "Test_Dialogue.txt", "Test_Thief.txt", "Test_Witch.txt",
              "unTest_Bartender.txt", "unTest_Noble.txt", "unTest_Shady.txt",
              "unTest_Shopkeep.txt", "unTest_Sleeping.txt", "unTest_Slouch.txt", "unTest_View.txt"}

CELL_SPLIT = re.compile(r'\|(?=(?:[^"]*"[^"]*")*[^"]*$)')

def repair_mixed(raw):
    """utf-8 为主, 个别 cp1252 孤字节(如 0x92=')修复为对应 Unicode"""
    out = []
    i, n = 0, len(raw)
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

def read_lines(fn):
    raw = open(os.path.join(SRC, fn), "rb").read()
    try:
        txt = raw.decode("utf-8")
        enc = "utf-8"
    except UnicodeDecodeError:
        txt = repair_mixed(raw)
        enc = "mixed+cp1252"
    return txt.split("\r\n" if fn not in LF_FILES else "\n"), enc

def detect_layout(fn, lines):
    """返回 (meta_rows, text_cols, col_names)"""
    name = fn[:-4]
    if name.startswith("delusionItemText"):
        # 行0 示例注释, 行1 表头: 0: Item ID | 1: Poor Name | 2: Poor Description | ...
        header = lines[1]
        cols = CELL_SPLIT.split(header)
        text_cols = [i for i, c in enumerate(cols) if not c.strip().startswith("0:")]
        return 2, text_cols, cols
    if name == "bookData_AllLanguages":
        cols = CELL_SPLIT.split(lines[0])
        text_cols = [i for i, c in enumerate(cols) if "English" in c]
        return 1, text_cols, cols
    if name == "generalData_AllLanguages":
        cols = CELL_SPLIT.split(lines[0])
        text_cols = [i for i, c in enumerate(cols) if "English" in c]
        return 1, text_cols, cols
    # 对话类(含 delusionTasks): 行0 元数据, 行1 表头 ID|English|... 或 20: English
    header = lines[1]
    cols = CELL_SPLIT.split(header)
    text_cols = [i for i, c in enumerate(cols) if "English" in c]
    return 2, text_cols, cols

rows_out = []
stats = []
context = []
for fn in sorted(os.listdir(SRC)):
    if not fn.endswith(".txt") or fn in SKIP_FILES:
        continue
    lines, enc = read_lines(fn)
    meta_rows, text_cols, col_names = detect_layout(fn, lines)
    data_name = fn[:-4]
    n_cells = n_chars = 0
    context.append(f"######## {data_name} (enc={enc}, rows={len(lines)}, text_cols={[col_names[i] for i in text_cols]})")
    for r in range(meta_rows):
        context.append(f"  META[{r}] {lines[r][:200]}")
    for ri in range(meta_rows, len(lines)):
        line = lines[ri]
        if not line.strip():
            continue
        cells = CELL_SPLIT.split(line)
        context.append(f"  DATA[{ri}] {line[:180]}")
        row_id = cells[0].strip() if cells else ""
        for ci in text_cols:
            if ci >= len(cells):
                continue
            val = cells[ci]
            # 去引号检查(保留原样, 只提取内容判断是否值得翻译)
            stripped = val.strip().strip('"')
            if not stripped or stripped == "None" or stripped.startswith("#"):
                continue
            # 纯标记/占位符跳过
            if re.fullmatch(r"[<>=\-_. ]*", stripped):
                continue
            key = f"{row_id}::{col_names[ci].strip()}" if col_names[ci].strip() else f"{row_id}::col{ci}"
            rows_out.append({
                "file": data_name, "row": ri, "col": ci, "key": key,
                "en": val, "zh": "",
            })
            n_cells += 1
            n_chars += len(stripped)
    stats.append((data_name, len(lines), n_cells, n_chars, enc))

# 写 TSV
def esc(s):
    return s.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r")

tsv_path = os.path.join(OUT, "all_texts.tsv")
with open(tsv_path, "w", encoding="utf-8", newline="") as f:
    f.write("DataName\tRow\tCol\tCellKey\tEnglish\tChinese\n")
    for r in rows_out:
        f.write(f"{r['file']}\t{r['row']}\t{r['col']}\t{esc(r['key'])}\t{esc(r['en'])}\t\n")

with open(os.path.join(OUT, "stats.txt"), "w", encoding="utf-8") as f:
    total_c = total_n = 0
    for name, nrows, ncells, nchars, enc in stats:
        f.write(f"{name:36s} rows={nrows:>5} cells={ncells:>5} chars={nchars:>8} enc={enc}\n")
        total_c += ncells; total_n += nchars
    f.write(f"\nTOTAL: {len(stats)} files, {total_c} cells, {total_n:,} chars\n")

with open(os.path.join(OUT, "context_notes.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(context))

print(f"提取完成: {len(stats)} 文件, {total_c} 单元格, {total_n:,} 字符")
print("输出:", tsv_path)
