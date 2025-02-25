# main.py
# This script allows the user to choose which script to run.
import os
import sys
import json
from logo import print_logo
from colorama import Fore, Style, init
import ctypes
from ctypes import windll
import locale
import platform

# 只在 Windows 系统上导入 windll
if platform.system() == 'Windows':
    from ctypes import windll

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
    "MENU": "📋",
    "ARROW": "➜",
    "LANG": "🌐",
    "UPDATE": "🔄"
}

class Translator:
    def __init__(self):
        self.translations = {}
        self.current_language = self._detect_system_language()
        self.fallback_language = 'en'  # Fallback language if translation is missing
        self.load_translations()
    
    def _detect_system_language(self):
        """检测系统语言"""
        system = platform.system()
        
        if system == 'Windows':
            return self._detect_windows_language()
        elif system == 'Darwin':  # macOS
            return self._detect_macos_language()
        elif system == 'Linux':
            return self._detect_linux_language()
        else:
            return 'en'  # 默认英语
    
    def _detect_windows_language(self):
        """检测 Windows 系统语言"""
        try:
            # 确保我们在 Windows 上
            if not hasattr(ctypes, 'windll'):
                return 'en'
                
            # 获取键盘布局
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            threadid = user32.GetWindowThreadProcessId(hwnd, 0)
            layout_id = user32.GetKeyboardLayout(threadid) & 0xFFFF
            
            # 根据键盘布局 ID 判断语言
            if layout_id == 0x0804:
                return 'zh_CN'  # 简体中文
            elif layout_id == 0x0404:
                return 'zh_TW'  # 繁体中文
            else:
                return 'en'  # 默认英语
        except Exception as e:
            print(f"Error detecting Windows language: {e}")
            return 'en'
    
    def _detect_macos_language(self):
        """检测 macOS 系统语言"""
        try:
            # 使用 defaults 命令获取系统语言设置
            import subprocess
            result = subprocess.run(['defaults', 'read', '-g', 'AppleLanguages'], 
                                   capture_output=True, text=True)
            output = result.stdout.strip()
            
            # 解析输出
            if 'zh-Hans' in output:
                return 'zh_CN'  # 简体中文
            elif 'zh-Hant' in output or 'zh_TW' in output:
                return 'zh_TW'  # 繁体中文
            else:
                return 'en'  # 默认英语
        except Exception as e:
            print(f"Error detecting macOS language: {e}")
            return 'en'
    
    def _detect_linux_language(self):
        """检测 Linux 系统语言"""
        try:
            # 检查环境变量
            lang = os.environ.get('LANG', '').lower()
            if lang.startswith('zh_cn'):
                return 'zh_CN'
            elif lang.startswith('zh_tw'):
                return 'zh_TW'
            else:
                return 'en'
        except Exception as e:
            print(f"Error detecting Linux language: {e}")
            return 'en'
    
    def load_translations(self):
        """Load all available translations"""
        try:
            locales_dir = os.path.join(os.path.dirname(__file__), 'locales')
            if hasattr(sys, '_MEIPASS'):
                locales_dir = os.path.join(sys._MEIPASS, 'locales')
            
            if not os.path.exists(locales_dir):
                print(f"{Fore.RED}{EMOJI['ERROR']} Locales directory not found{Style.RESET_ALL}")
                return

            for file in os.listdir(locales_dir):
                if file.endswith('.json'):
                    lang_code = file[:-5]  # Remove .json
                    try:
                        with open(os.path.join(locales_dir, file), 'r', encoding='utf-8') as f:
                            self.translations[lang_code] = json.load(f)
                    except (json.JSONDecodeError, UnicodeDecodeError) as e:
                        print(f"{Fore.RED}{EMOJI['ERROR']} Error loading {file}: {e}{Style.RESET_ALL}")
                        continue
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} Failed to load translations: {e}{Style.RESET_ALL}")
    
    def get(self, key, **kwargs):
        """Get translated text with fallback support"""
        try:
            # Try current language
            result = self._get_translation(self.current_language, key)
            if result == key and self.current_language != self.fallback_language:
                # Try fallback language if translation not found
                result = self._get_translation(self.fallback_language, key)
            return result.format(**kwargs) if kwargs else result
        except Exception:
            return key
    
    def _get_translation(self, lang_code, key):
        """Get translation for a specific language"""
        try:
            keys = key.split('.')
            value = self.translations.get(lang_code, {})
            for k in keys:
                if isinstance(value, dict):
                    value = value.get(k, key)
                else:
                    return key
            return value
        except Exception:
            return key
    
    def set_language(self, lang_code):
        """Set current language with validation"""
        if lang_code in self.translations:
            self.current_language = lang_code
            return True
        return False

    def get_available_languages(self):
        """Get list of available languages"""
        return list(self.translations.keys())

# 创建翻译器实例
translator = Translator()

def print_menu():
    """打印菜单选项"""
    print(f"\n{Fore.CYAN}{EMOJI['MENU']} {translator.get('menu.title')}:{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'─' * 40}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}0{Style.RESET_ALL}. {EMOJI['ERROR']} {translator.get('menu.exit')}")
    print(f"{Fore.GREEN}1{Style.RESET_ALL}. {EMOJI['RESET']} {translator.get('menu.reset')}")
    print(f"{Fore.GREEN}2{Style.RESET_ALL}. {EMOJI['SUCCESS']} {translator.get('menu.register')}")
    print(f"{Fore.GREEN}3{Style.RESET_ALL}. {EMOJI['SUCCESS']} {translator.get('menu.register_manual')}")
    print(f"{Fore.GREEN}4{Style.RESET_ALL}. {EMOJI['ERROR']} {translator.get('menu.quit')}")
    print(f"{Fore.GREEN}5{Style.RESET_ALL}. {EMOJI['LANG']} {translator.get('menu.select_language')}")
    print(f"{Fore.GREEN}6{Style.RESET_ALL}. {EMOJI['UPDATE']} {translator.get('menu.disable_auto_update')}")
    print(f"{Fore.YELLOW}{'─' * 40}{Style.RESET_ALL}")

def select_language():
    """Language selection menu"""
    print(f"\n{Fore.CYAN}{EMOJI['LANG']} {translator.get('menu.select_language')}:{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'─' * 40}{Style.RESET_ALL}")
    
    languages = translator.get_available_languages()
    for i, lang in enumerate(languages):
        lang_name = translator.get(f"languages.{lang}")
        print(f"{Fore.GREEN}{i}{Style.RESET_ALL}. {lang_name}")
    
    try:
        choice = input(f"\n{EMOJI['ARROW']} {Fore.CYAN}{translator.get('menu.input_choice', choices=f'0-{len(languages)-1}')}: {Style.RESET_ALL}")
        if choice.isdigit() and 0 <= int(choice) < len(languages):
            translator.set_language(languages[int(choice)])
            return True
        else:
            print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('menu.invalid_choice')}{Style.RESET_ALL}")
            return False
    except (ValueError, IndexError):
        print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('menu.invalid_choice')}{Style.RESET_ALL}")
        return False

def main():
    print_logo()
    print_menu()
    
    while True:
        try:
            choice = input(f"\n{EMOJI['ARROW']} {Fore.CYAN}{translator.get('menu.input_choice', choices='0-6')}: {Style.RESET_ALL}")

            if choice == "0":
                print(f"\n{Fore.YELLOW}{EMOJI['INFO']} {translator.get('menu.exit')}...{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{'═' * 50}{Style.RESET_ALL}")
                return
            elif choice == "1":
                import reset_machine_manual
                reset_machine_manual.run(translator)
                break
            elif choice == "2":
                import cursor_register
                cursor_register.main(translator)
                break
            elif choice == "3":
                import cursor_register_manual
                cursor_register_manual.main(translator)
                break
            elif choice == "4":
                import quit_cursor
                quit_cursor.quit_cursor(translator)
                break
            elif choice == "5":
                if select_language():
                    print_menu()
                continue
            elif choice == "6":
                import disable_auto_update
                disable_auto_update.run(translator)
                break
            else:
                print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('menu.invalid_choice')}{Style.RESET_ALL}")
                print_menu()

        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}{EMOJI['INFO']} {translator.get('menu.program_terminated')}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'═' * 50}{Style.RESET_ALL}")
            return
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('menu.error_occurred', error=str(e))}{Style.RESET_ALL}")
            break

    print(f"\n{Fore.CYAN}{'═' * 50}{Style.RESET_ALL}")
    input(f"{EMOJI['INFO']} {translator.get('menu.press_enter')}...{Style.RESET_ALL}")

if __name__ == "__main__":
    main()