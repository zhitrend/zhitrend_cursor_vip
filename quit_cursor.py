import psutil
import time
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
    "PROCESS": "⚙️",
    "WAIT": "⏳"
}

class CursorQuitter:
    def __init__(self, timeout=5):
        self.timeout = timeout
        
    def quit_cursor(self):
        """温和地关闭 Cursor 进程"""
        try:
            print(f"{Fore.CYAN}{EMOJI['PROCESS']} Start Quitting Cursor | 开始退出 Cursor...{Style.RESET_ALL}")
            cursor_processes = []
            
            # 收集所有 Cursor 进程
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'].lower() in ['cursor.exe', 'cursor']:
                        cursor_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if not cursor_processes:
                print(f"{Fore.GREEN}{EMOJI['INFO']} No Running Cursor Process | 未发现运行中的 Cursor 进程{Style.RESET_ALL}")
                return True

            # 温和地请求进程终止
            for proc in cursor_processes:
                try:
                    if proc.is_running():
                        print(f"{Fore.YELLOW}{EMOJI['PROCESS']} Terminating Process | 正在终止进程 {proc.pid}...{Style.RESET_ALL}")
                        proc.terminate()  # 发送终止信号
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # 等待进程自然终止
            print(f"{Fore.CYAN}{EMOJI['WAIT']} Waiting for Process to Exit | 等待进程退出...{Style.RESET_ALL}")
            start_time = time.time()
            while time.time() - start_time < self.timeout:
                still_running = []
                for proc in cursor_processes:
                    try:
                        if proc.is_running():
                            still_running.append(proc)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                if not still_running:
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} All Cursor Processes Closed | 所有 Cursor 进程已正常关闭{Style.RESET_ALL}")
                    return True
                    
                # 等待一小段时间再检查
                time.sleep(0.5)
                
            # 如果超时后仍有进程在运行
            if still_running:
                process_list = ", ".join([str(p.pid) for p in still_running])
                print(f"{Fore.RED}{EMOJI['ERROR']} Process Timeout | 以下进程未能在规定时间内关闭: {process_list}{Style.RESET_ALL}")
                return False
                
            return True

        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} Error Occurred | 关闭 Cursor 进程时发生错误: {str(e)}{Style.RESET_ALL}")
            return False

def quit_cursor(timeout=5):
    """便捷函数，用于直接调用退出功能"""
    quitter = CursorQuitter(timeout)
    return quitter.quit_cursor()

if __name__ == "__main__":
    quit_cursor()