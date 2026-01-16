# ⌨️ VS Code Family Keybindings Sync

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS-lightgrey.svg)]()

**一键同步 VS Code、Cursor、Windsurf 等编辑器的快捷键配置。**

基于文件系统 **软链接 (Symlink)** 机制，建立唯一的配置源。在任一编辑器修改快捷键，所有编辑器实时生效。

---

## ✨ 功能特性

* **自动探测**：支持 VS Code, Cursor, Windsurf, Kiro, Antigravity 等。
* **实时同步**：基于 `ln -s`，毫秒级响应。
* **安全备份**：自动备份旧配置，防止数据丢失。

---

## 🚀 运行演示

```console
$ python3 sync-editors.py

   🔍 正在扫描已安装的编辑器...
      ✅ [发现] VS Code
      ✅ [发现] Cursor
      ✅ [发现] Windsurf
      ✅ [发现] Kiro
      ✅ [发现] Antigravity

   👉 请选择作为 [源 (Source)] 的编辑器:
      [1] VS Code
      [2] Cursor
      [3] Windsurf
      [4] Kiro
      [5] Antigravity

   ⌨️  请输入编号: 2

   🎯 已选择源: Cursor
      即将把 [Cursor] 的配置链接给其他 4 个编辑器。
      (旧配置将自动备份)

   ❓ 确认执行? (y/n): y
   
   🚀 同步完成！
