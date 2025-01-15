from colorama import Fore, Style, init
from dotenv import load_dotenv
import os

# 加載環境變量獲取版本號
load_dotenv()
version = os.getenv('VERSION', '1.0.0')

# 初始化 colorama
init()

CURSOR_LOGO = f"""
{Fore.CYAN}
   ██████╗██╗   ██╗██████╗ ███████╗ ██████╗ ██████╗      ██████╗ ██████╗  ██████╗   
  ██╔════╝██║   ██║██╔══██╗██╔════╝██╔═══██╗██╔══██╗     ██╔══██╗██╔══██╗██╔═══██╗  
  ██║     ██║   ██║██████╔╝███████╗██║   ██║██████╔╝     ██████╔╝██████╔╝██║   ██║  
  ██║     ██║   ██║██╔══██╗╚════██║██║   ██║██╔══██╗     ██╔═══╝ ██╔══██╗██║   ██║  
  ╚██████╗╚██████╔╝██║  ██║███████║╚██████╔╝██║  ██║     ██║     ██║  ██║╚██████╔╝  
   ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝     ╚═╝     ╚═╝  ╚═╝ ╚═════╝  
{Fore.YELLOW}
                Pro Version Activator v{version}
{Fore.GREEN}
                Author: Pin Studios | yeongpin
{Fore.RED}
        Press 4 to change language | 按下 4 键切换语言
{Style.RESET_ALL}
    """

def print_logo():
    print(CURSOR_LOGO)


if __name__ == "__main__":
    print_logo()