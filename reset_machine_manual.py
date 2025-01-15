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

# 定义emoji常量
EMOJI = {
    "FILE": "📄",
    "BACKUP": "💾",
    "SUCCESS": "✅",
    "ERROR": "❌",
    "INFO": "ℹ️",
    "RESET": "🔄",
}

class MachineIDResetter:
    def __init__(self, translator=None):
        self.translator = translator

        # 判断操作系统
        if sys.platform == "win32":  # Windows
            appdata = os.getenv("APPDATA")
            if appdata is None:
                raise EnvironmentError("APPDATA Environment Variable Not Set")
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
        elif sys.platform == "linux":  # Linux
            self.db_path = os.path.abspath(os.path.expanduser(
                "~/.config/Cursor/User/globalStorage/storage.json"
            ))
            self.sqlite_path = os.path.abspath(os.path.expanduser(
                "~/.config/Cursor/User/globalStorage/state.vscdb"
            ))
        else:
            raise NotImplementedError(f"Not Supported OS: {sys.platform}")

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
            print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('reset.updating_sqlite')}...{Style.RESET_ALL}")
            
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ItemTable (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)

            updates = [
                (key, value) for key, value in new_ids.items()
            ]

            for key, value in updates:
                cursor.execute("""
                    INSERT OR REPLACE INTO ItemTable (key, value) 
                    VALUES (?, ?)
                """, (key, value))
                print(f"{EMOJI['INFO']} {Fore.CYAN}{self.translator.get('reset.updating_pair')}: {key}{Style.RESET_ALL}")

            conn.commit()
            conn.close()
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('reset.sqlite_success')}{Style.RESET_ALL}")
            return True

        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('reset.sqlite_error', error=str(e))}{Style.RESET_ALL}")
            return False

    def reset_machine_ids(self):
        """重置机器ID并备份原文件"""
        try:
            print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('reset.checking')}...{Style.RESET_ALL}")

            if not os.path.exists(self.db_path):
                print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('reset.not_found')}: {self.db_path}{Style.RESET_ALL}")
                return False

            if not os.access(self.db_path, os.R_OK | os.W_OK):
                print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('reset.no_permission')}{Style.RESET_ALL}")
                return False

            print(f"{Fore.CYAN}{EMOJI['FILE']} {self.translator.get('reset.reading')}...{Style.RESET_ALL}")
            with open(self.db_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            backup_path = self.db_path + ".bak"
            if not os.path.exists(backup_path):
                print(f"{Fore.YELLOW}{EMOJI['BACKUP']} {self.translator.get('reset.creating_backup')}: {backup_path}{Style.RESET_ALL}")
                shutil.copy2(self.db_path, backup_path)
            else:
                print(f"{Fore.YELLOW}{EMOJI['INFO']} {self.translator.get('reset.backup_exists')}{Style.RESET_ALL}")

            print(f"{Fore.CYAN}{EMOJI['RESET']} {self.translator.get('reset.generating')}...{Style.RESET_ALL}")
            new_ids = self.generate_new_ids()

            config.update(new_ids)

            print(f"{Fore.CYAN}{EMOJI['FILE']} {self.translator.get('reset.saving_json')}...{Style.RESET_ALL}")
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)

            self.update_sqlite_db(new_ids)

            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('reset.success')}{Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}{self.translator.get('reset.new_id')}:{Style.RESET_ALL}")
            for key, value in new_ids.items():
                print(f"{EMOJI['INFO']} {key}: {Fore.GREEN}{value}{Style.RESET_ALL}")

            return True

        except PermissionError as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('reset.permission_error', error=str(e))}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{EMOJI['INFO']} {self.translator.get('reset.run_as_admin')}{Style.RESET_ALL}")
            return False
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('reset.process_error', error=str(e))}{Style.RESET_ALL}")
            return False

def run(translator=None):
    """便捷函数，用于直接调用重置功能"""
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{EMOJI['RESET']} {translator.get('reset.title')}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

    resetter = MachineIDResetter(translator)  # 正確傳遞 translator
    resetter.reset_machine_ids()

    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    input(f"{EMOJI['INFO']} {translator.get('reset.press_enter')}...")

if __name__ == "__main__":
    from main import translator as main_translator
    run(main_translator)