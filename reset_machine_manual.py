import os
import sys
import json
import uuid
import hashlib
import shutil
import sqlite3
from colorama import Fore, Style, init

# 初始化colorama
init()

# 定义emoji和颜色常量
EMOJI = {
    "FILE": "📄",
    "BACKUP": "💾",
    "SUCCESS": "✅",
    "ERROR": "❌",
    "INFO": "ℹ️",
    "RESET": "🔄",
}

class MachineIDResetter:
    def __init__(self):

        # 判断操作系统
        if sys.platform == "win32":  # Windows
            appdata = os.getenv("APPDATA")
            if appdata is None:
                raise EnvironmentError("APPDATA Environment Variable Not Set | APPDATA 环境变量未设置")
            self.db_path = os.path.join(
                appdata, "Cursor", "User", "globalStorage", "storage.json"
            )
            self.sqlite_path = os.path.join(
                appdata, "Cursor", "User", "globalStorage", "state.vscdb"
            )
        elif sys.platform == "darwin":  # macOS
            self.db_path = os.path.abspath(os.path.expanduser(
                "~/Library/Application Support/Cursor/User/globalStorage/storage.json"
            ))
            self.sqlite_path = os.path.abspath(os.path.expanduser(
                "~/Library/Application Support/Cursor/User/globalStorage/state.vscdb"
            ))
        elif sys.platform == "linux":  # Linux 和其他类Unix系统
            self.db_path = os.path.abspath(os.path.expanduser(
                "~/.config/Cursor/User/globalStorage/storage.json"
            ))
            self.sqlite_path = os.path.abspath(os.path.expanduser(
                "~/.config/Cursor/User/globalStorage/state.vscdb"
            ))
        else:
            raise NotImplementedError(f"Not Supported Os| 不支持的操作系统: {sys.platform}")

    def generate_new_ids(self):
        """生成新的机器ID"""
        # 生成新的UUID
        dev_device_id = str(uuid.uuid4())

        # 生成新的machineId (64个字符的十六进制)
        machine_id = hashlib.sha256(os.urandom(32)).hexdigest()

        # 生成新的macMachineId (128个字符的十六进制)
        mac_machine_id = hashlib.sha512(os.urandom(64)).hexdigest()

        # 生成新的sqmId
        sqm_id = "{" + str(uuid.uuid4()).upper() + "}"

        return {
            "telemetry.devDeviceId": dev_device_id,
            "telemetry.macMachineId": mac_machine_id,
            "telemetry.machineId": machine_id,
            "telemetry.sqmId": sqm_id,
            "storage.serviceMachineId": dev_device_id,  # 添加 storage.serviceMachineId
        }

    def update_sqlite_db(self, new_ids):
        """更新 SQLite 数据库中的机器ID"""
        try:
            print(f"{Fore.CYAN}{EMOJI['INFO']} Updating SQLite Database | 正在更新 SQLite 数据库...{Style.RESET_ALL}")
            
            # 创建数据库连接
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()

            # 确保表存在
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ItemTable (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)

            # 准备更新数据
            updates = [
                (key, value) for key, value in new_ids.items()
            ]

            # 使用参数化查询来避免 SQL 注入和处理长文本
            for key, value in updates:
                cursor.execute("""
                    INSERT OR REPLACE INTO ItemTable (key, value) 
                    VALUES (?, ?)
                """, (key, value))
                print(f"{EMOJI['INFO']} {Fore.CYAN}Updating Key-Value Pair | 更新键值对: {key}{Style.RESET_ALL}")

            # 提交更改并关闭连接
            conn.commit()
            conn.close()
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} SQLite Database Updated Successfully | 数据库更新成功！{Style.RESET_ALL}")
            return True

        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} SQLite Database Update Failed | 数据库更新失败: {str(e)}{Style.RESET_ALL}")
            return False

    def reset_machine_ids(self):
        """重置机器ID并备份原文件"""
        try:
            print(f"{Fore.CYAN}{EMOJI['INFO']} Checking Config File | 正在检查配置文件...{Style.RESET_ALL}")

            # 检查JSON文件是否存在
            if not os.path.exists(self.db_path):
                print(
                    f"{Fore.RED}{EMOJI['ERROR']} Config File Not Found | 配置文件不存在: {self.db_path}{Style.RESET_ALL}"
                )
                return False

            # 检查文件权限
            if not os.access(self.db_path, os.R_OK | os.W_OK):
                print(
                    f"{Fore.RED}{EMOJI['ERROR']} Cannot Read or Write Config File, Please Check File Permissions | 无法读写配置文件，请检查文件权限！{Style.RESET_ALL}"
                )
                return False

            # 读取现有配置
            print(f"{Fore.CYAN}{EMOJI['FILE']} Reading Current Config | 读取当前配置...{Style.RESET_ALL}")
            with open(self.db_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            # 只在没有备份文件时创建备份
            backup_path = self.db_path + ".bak"
            if not os.path.exists(backup_path):
                print(
                    f"{Fore.YELLOW}{EMOJI['BACKUP']} Creating Config Backup |  创建配置备份: {backup_path}{Style.RESET_ALL}"
                )
                shutil.copy2(self.db_path, backup_path)
            else:
                print(
                    f"{Fore.YELLOW}{EMOJI['INFO']} Backup File Already Exists, Skipping Backup Step | 已存在备份文件，跳过备份步骤{Style.RESET_ALL}"
                )

            # 生成新的ID
            print(f"{Fore.CYAN}{EMOJI['RESET']} Generating New Machine ID | 生成新的机器标识...{Style.RESET_ALL}")
            new_ids = self.generate_new_ids()

            # 更新配置
            config.update(new_ids)

            # 保存新配置到 JSON
            print(f"{Fore.CYAN}{EMOJI['FILE']} Saving New Config to JSON | 保存新配置到 JSON...{Style.RESET_ALL}")
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)

            # 更新 SQLite 数据库
            self.update_sqlite_db(new_ids)

            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Machine ID Reset Successfully | 机器标识重置成功！{Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}New Machine ID | 新的机器标识:{Style.RESET_ALL}")
            for key, value in new_ids.items():
                print(f"{EMOJI['INFO']} {key}: {Fore.GREEN}{value}{Style.RESET_ALL}")

            return True

        except PermissionError as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} Permission Error | 权限错误: {str(e)}{Style.RESET_ALL}")
            print(
                f"{Fore.YELLOW}{EMOJI['INFO']} Please Try Running This Program as Administrator | 请尝试以管理员身份运行此程序{Style.RESET_ALL}"
            )
            return False
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} Reset Process Error | 重置过程出错: {str(e)}{Style.RESET_ALL}")
            return False

def run():
    """Main function to be called from main.py"""
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{EMOJI['RESET']} Cursor Machine ID Reset Tool | Cursor 机器标识重置工具{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

    resetter = MachineIDResetter()
    resetter.reset_machine_ids()

    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    input(f"{EMOJI['INFO']} Press Enter to Exit | 按回车键退出...")

if __name__ == "__main__":
    run()