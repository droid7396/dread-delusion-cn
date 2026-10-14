# -*- coding: utf-8 -*-
"""共享路径配置: 所有脚本 import common 取路径; 本地差异放 config.local.ini (不入库)"""
import os
import configparser

ROOT = os.path.dirname(os.path.abspath(__file__))

# 仓库内固定路径
TEXT_IN  = os.path.join(ROOT, "Text136")            # 游戏原文导出 (list_textassets.py 生成)
TEXT_OUT = os.path.join(ROOT, "Out136")             # 写回文本产物 (writeback.py 生成)
BYFILE   = os.path.join(ROOT, "translate", "byfile")
FONTS    = os.path.join(ROOT, "fonts")
ASSETS_NEW   = os.path.join(ROOT, "resources.assets.new")    # writeback 产物
ASSETS_FINAL = os.path.join(ROOT, "resources.assets.final")  # inject_fonts/apply_cnfont 产物
BUNDLE   = os.path.join(ROOT, "UnityFontGen", "Assets", "Out", "cnfont.bundle")
FUSION_TTF  = os.path.join(FONTS, "fusion12", "fusion-pixel-12px-proportional-zh_hans.ttf")
SYMBOLA_TTF = os.path.join(FONTS, "symbola_orig.ttf")

# 本地配置 (游戏路径等)
_cfg = configparser.ConfigParser()
_cfg.read(os.path.join(ROOT, "config.local.ini"), encoding="utf-8")
GAME_DATA = _cfg.get("game", "data_dir",
                     fallback=r"C:\Games\Dread Delusion\windows_content\Dread Delusion_Data")
GAME_ASSETS     = os.path.join(GAME_DATA, "resources.assets")
GAME_ASSETS_BAK = GAME_ASSETS + ".bak"
