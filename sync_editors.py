#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
import time
from pathlib import Path

# Configuration of supported editors
# Key: ID, Value: Dict with Name, AppSupportPath, ExtensionPath, ProcessName
EDITORS_CONFIG = {
    "vscode": {
        "name": "VS Code",
        "app_support": "~/Library/Application Support/Code/User",
        "extensions": "~/.vscode/extensions",
        "process_name": "Electron"  # VSCode often appears as Electron, but we can refine this
    },
    "cursor": {
        "name": "Cursor",
        "app_support": "~/Library/Application Support/Cursor/User",
        "extensions": "~/.cursor/extensions",
        "process_name": "Cursor"
    },
    "windsurf": {
        "name": "Windsurf",
        "app_support": "~/Library/Application Support/Windsurf/User",
        "extensions": "~/.windsurf/extensions",
        "process_name": "Windsurf"
    },
    "kiro": {
        "name": "Kiro",
        "app_support": "~/Library/Application Support/Kiro/User",
        "extensions": "~/.kiro/extensions",
        "process_name": "Kiro"
    },
    "antigravity": {
        "name": "Antigravity",
        "app_support": "~/Library/Application Support/Antigravity/User",
        "extensions": "~/.antigravity/extensions",
        "process_name": "Antigravity"
    },
    "trae": {
        "name": "Trae",
        "app_support": "~/Library/Application Support/Trae/User",
        "extensions": "~/.trae/extensions",
        "process_name": "Trae"
    },
    "qoder": {
        "name": "Qoder",
        "app_support": "~/Library/Application Support/Qoder/User",
        "extensions": "~/.qoder/extensions",
        "process_name": "Qoder"
    }
}

def expand_path(path_str):
    return Path(os.path.expanduser(path_str))

def get_installed_editors():
    installed = []
    print("正在扫描已安装的编辑器...")
    for key, config in EDITORS_CONFIG.items():
        app_support = expand_path(config["app_support"])
        # extensions = expand_path(config["extensions"]) 
        # Checking AppSupport User dir is the most reliable way to see if valid config exists
        if app_support.exists():
            installed.append((key, config))
            print(f"  [发现] {config['name']}")
        else:
            # Check if parent exists (maybe User dir generally created after first run)
            if app_support.parent.exists():
                installed.append((key, config))
                print(f"  [发现] {config['name']} (仅主目录)")
    return installed

def backup_path(path: Path):
    if not path.exists() and not path.is_symlink():
        return
    
    timestamp = int(time.time())
    backup_name = f"{path.name}.backup.{timestamp}"
    backup_file = path.parent / backup_name
    
    if path.is_symlink():
        print(f"  [备份] 移除软链接: {path}")
        path.unlink()
    else:
        print(f"  [备份] 移动 {path} -> {backup_file}")
        shutil.move(str(path), str(backup_file))

def create_symlink(source: Path, target: Path):
    if target.exists() or target.is_symlink():
        backup_path(target)
    
    # Ensure parent exists
    target.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"  [链接] {target} -> {source}")
    target.symlink_to(source)

def get_running_pids(process_name_substr):
    # This is a simple grep. For specific apps, might need exact mapping.
    # macOS 'pgrep -f' matches against full argument list
    try:
        current_pid = os.getpid()
        result = subprocess.check_output(["pgrep", "-f", process_name_substr])
        pids = [int(p) for p in result.decode().split() if int(p) != current_pid]
        return pids
    except subprocess.CalledProcessError:
        return []

def restart_app(editor_config):
    # Simplified restart: Kill and let user restart, or try 'open'?
    # The requirement is "restart". 
    # 'open -a ApplicationName' works if we know the app name.
    
    # Heuristic: Match process name
    # Note: VSCode process is 'Electron' often, but pgrep -f 'App path' works better.
    # We will try to kill known PIDs.
    
    # Identify PIDs
    name = editor_config['name']
    pids = get_running_pids(name)
    
    if not pids:
        print(f"  {name} 未运行。")
        return

    print(f"  检测到 {name} 正在运行 (PID: {pids})，正在关闭...")
    for pid in pids:
        try:
            os.kill(pid, 15) # SIGTERM
        except OSError:
            pass
    
    # Wait for exit
    time.sleep(2)
    
    # Attempt to restart
    # Best guess application name in /Applications
    app_path = Path(f"/Applications/{name}.app")
    if app_path.exists():
        print(f"  正在重启 {name}...")
        subprocess.call(["open", str(app_path)])
    else:
        print(f"  未在 /Applications 找到 {name}.app，请手动重启。")

def register_cli():
    # Create a wrapper script in ~/.local/bin or ask to add alias
    script_path = Path(__file__).resolve()
    shell = os.environ.get("SHELL", "/bin/zsh")
    rc_file = Path(os.path.expanduser("~/.zshrc")) if "zsh" in shell else Path(os.path.expanduser("~/.bashrc"))
    
    alias_line = f'alias sync-editors="python3 {script_path}"'
    
    if rc_file.exists():
        content = rc_file.read_text()
        if str(script_path) in content:
            print(f"  CID配置已存在于 {rc_file}")
            return

        with open(rc_file, "a") as f:
            f.write(f"\n# Added by Sync Editors Script\n{alias_line}\n")
        print(f"  已添加 alias 到 {rc_file}。请运行 'source {rc_file}' 或重启终端生效。")
    else:
        print(f"  未找到 shell 配置文件 {rc_file}。请手动添加 alias: \n  {alias_line}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--install":
        register_cli()
        return

    print("=== 编辑器配置同步工具 ===")
    installed = get_installed_editors()
    
    if not installed:
        print("未找到支持的编辑器。")
        return

    print("\n请选择作为 [源 (Source)] 的编辑器 (其配置将被分发给其他应用):")
    for i, (key, config) in enumerate(installed):
        print(f"  [{i+1}] {config['name']}")

    try:
        choice = input("\n请输入编号: ")
        idx = int(choice) - 1
        if idx < 0 or idx >= len(installed):
            raise ValueError
    except ValueError:
        print("无效输入。")
        return

    source_key, source_config = installed[idx]
    print(f"\n已选择源: {source_config['name']}")
    print("即将把此配置同步给其他已安装的编辑器 (旧配置将被备份)。")
    confirm = input("确认执行? (y/n): ")
    if confirm.lower() != 'y':
        print("取消操作。")
        return

    source_app_support = expand_path(source_config["app_support"])
    source_extensions = expand_path(source_config["extensions"])

    if not source_app_support.exists():
         print(f"警告: 源配置目录不存在 {source_app_support}")
         # Might proceed if user really wants to sync extensions only? But unlikely.
         return
         
    for key, config in installed:
        if key == source_key:
            continue
            
        print(f"\n正在处理 {config['name']}...")
        
        # Sync User Config
        curr_app_support = expand_path(config["app_support"])
        create_symlink(source_app_support, curr_app_support)
        
        # Sync Extensions
        # Only sync extensions if source exists, otherwise we might wipe extensions for empty
        if source_extensions.exists():
            curr_extensions = expand_path(config["extensions"])
            create_symlink(source_extensions, curr_extensions)
        else:
            print(f"  源扩展目录 {source_extensions} 不存在，跳过扩展同步。")
            
        # Restart Process
        restart_app(config)

    print("\n同步完成！")

if __name__ == "__main__":
    main()
