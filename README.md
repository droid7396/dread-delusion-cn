# Dread Delusion 汉化（恐惧妄想）

《Dread Delusion》v1.3.6 的简体中文汉化工程。全文本汉化（对话/物品/任务/书籍/UI，约 12300 条），像素风字体（融合像素 12px），游戏内完整可读。

> **免责声明**：本工程仅供学习交流，游玩请支持正版。游戏文本与资产版权归原开发商（Lovely Hellplace / Dreadful Torque Games）所有。译文部分采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)。

## 使用方式

### 方式一：直接使用补丁（推荐普通玩家）
从 Release 页下载 `resources.assets`，覆盖到游戏目录 `Dread Delusion_Data\` 下即可。
卸载：Steam → 右键游戏 → 属性 → 已安装文件 → 验证文件完整性。

### 方式二：从源码构建（贡献者/自定义）
1. 安装 Python 3.10+，然后：
   ```
   pip install UnityPy Pillow fonttools
   ```
2. 复制 `config.example.ini` 为 `config.local.ini`，填入你的游戏数据目录。
3. 导出游戏原文基准（游戏更新后也需要）：
   ```
   py list_textassets.py    # 游戏 TextAsset -> Text136/
   py extract_texts.py      # 结构化提取 -> extract/
   ```
4. 翻译：编辑 `translate/byfile/*.tsv`（5 列：ID/Col/CellKey/English/Chinese）。
   - ID 为游戏表格语义行 ID（如 `citizen1`），重复行带 `#序号`
   - **引号铁律**：直引号 `"` 数量必须与 English 列同奇偶（写回器有守卫）
5. 构建并部署：
   ```
   py writeback.py      # byfile + Text136 -> resources.assets.new
   py inject_fonts.py   # 字体注入 -> resources.assets.final
   py apply_cnfont.py   # TMP 三件套替换
   copy resources.assets.final "<游戏目录>\Dread Delusion_Data\resources.assets"
   ```

## 字体（可选：重新生成 TMP 图集）

默认图集已随仓库提供（`UnityFontGen/Assets/Out/cnfont.bundle`）。仅当新增字符或更换字体时需要 Unity：
1. 安装 Unity 2022.3.60f1（需免费 Personal 许可证）
2. 把 `fonts/fusion12/fusion-pixel-12px-proportional-zh_hans.ttf` 复制为 `UnityFontGen/Assets/fusion.ttf`
3. 首次打开工程时导入 TMP Essentials（或从包内 Package Resources 手动解包）
4. 批处理生成：
   ```
   "Unity.exe" -batchmode -quit -projectPath <本仓库>\UnityFontGen -executeMethod FontGen.Generate -logFile gen.log
   ```

## 游戏版本更新后

1. Steam 更新游戏 → `py list_textassets.py` + `py extract_texts.py` 重新提取
2. 对照合并旧译文（按 CellKey），翻译新增/变更文本
3. `apply_cnfont.py` 顶部的三个 `path_id` 需按新版本重新定位
4. 核对 TMP 序列化结构是否随游戏更新变化

## 目录结构

```
translate/byfile/    译文源（22 个源文件对照表）
fonts/               融合像素 12px(OFL) + Symbola + 许可证
extract/             术语表(496条) + 世界观笔记
Text136/             原文基准（不入库，本地生成）
UnityFontGen/        Unity 字体生成工程
*.py                 构建管线（见上方四步）
```

## 致谢

- [融合像素字体 Fusion Pixel Font](https://github.com/TakWolf/fusion-pixel-font)（OFL）及其内嵌的 ark-pixel / cubic-11 / galmuri 字体
- [Symbola](https://www.fontspace.com/symbola-font-f2916)（公有领域），负责炼金符号渲染
- 日语化补丁与俄语本地化包的思路参考

## 许可

- 构建脚本：[MIT](LICENSE)
- 译文：CC BY-NC-SA 4.0
- 字体：各随附许可见 `fonts/fusion12/LICENSES/` 与 `fonts/fusion12/OFL.txt`
