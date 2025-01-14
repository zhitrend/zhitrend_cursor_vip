# main.py
# This script allows the user to choose which script to run.
from logo import print_logo
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
    "MENU": "📋",
    "ARROW": "➜",
}

def print_menu():
    """打印菜单选项"""
    print(f"\n{Fore.CYAN}{EMOJI['MENU']} Available Options | 可用选项:{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'─' * 40}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}0{Style.RESET_ALL}. {EMOJI['ERROR']} Exit Program | 退出程序")
    print(f"{Fore.GREEN}1{Style.RESET_ALL}. {EMOJI['RESET']} Reset Machine Manual | 重置机器标识")
    print(f"{Fore.GREEN}2{Style.RESET_ALL}. {EMOJI['RESET']} Register Cursor | 注册 Cursor")
    # 在这里添加更多选项
    print(f"{Fore.YELLOW}{'─' * 40}{Style.RESET_ALL}")

def main():
    print_logo()
    print_menu()
    
    while True:
        try:
            choice = input(f"\n{EMOJI['ARROW']} {Fore.CYAN}Enter your choice (0-2) | 输入选择 (0-2): {Style.RESET_ALL}")

            if choice == "0":
                print(f"\n{Fore.YELLOW}{EMOJI['INFO']} Exiting program... | 正在退出程序...{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{'═' * 50}{Style.RESET_ALL}")
                return  # 直接返回，不等待按键
            elif choice == "1":
                import reset_machine_manual
                reset_machine_manual.run()
                break
            elif choice == "2":
                import cursor_register
                cursor_register.main()
                break
            else:
                print(f"{Fore.RED}{EMOJI['ERROR']} Invalid choice. Please try again | 无效选择，请重试{Style.RESET_ALL}")
                print_menu()

        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}{EMOJI['INFO']} Program terminated by user | 程序被用户终止{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'═' * 50}{Style.RESET_ALL}")
            return  # 直接返回，不等待按键
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} An error occurred | 发生错误: {str(e)}{Style.RESET_ALL}")
            break

    # 只有在执行完其他选项后才显示按键退出提示
    print(f"\n{Fore.CYAN}{'═' * 50}{Style.RESET_ALL}")
    input(f"{EMOJI['INFO']} Press Enter to Exit | 按回车键退出...{Style.RESET_ALL}")

if __name__ == "__main__":
    main() 