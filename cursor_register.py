import os
from colorama import Fore, Style, init
import time
import random
from browser import BrowserManager
from control import BrowserControl
from cursor_auth import CursorAuth
from reset_machine_manual import MachineIDResetter

os.environ["PYTHONVERBOSE"] = "0"
os.environ["PYINSTALLER_VERBOSE"] = "0"

# 初始化colorama
init()

# 定义emoji和颜色常量
EMOJI = {
    'START': '🚀',
    'FORM': '📝',
    'VERIFY': '🔄',
    'PASSWORD': '🔑',
    'CODE': '📱',
    'DONE': '✨',
    'ERROR': '❌',
    'WAIT': '⏳',
    'SUCCESS': '✅',
    'MAIL': '��',
    'KEY': '🔐',
    'UPDATE': '🔄'
}

class CursorRegistration:
    def __init__(self):
        # 设置为显示模式
        os.environ['BROWSER_HEADLESS'] = 'False'
        self.browser_manager = BrowserManager()
        self.browser = None
        self.controller = None
        self.mail_url = "https://yopmail.com/zh/email-generator"
        self.sign_up_url = "https://authenticator.cursor.sh/sign-up"
        self.settings_url = "https://www.cursor.com/settings"
        self.email_address = None
        self.signup_tab = None
        self.email_tab = None
        
        # 账号信息
        self.password = self._generate_password()
        self.first_name = self._generate_name()
        self.last_name = self._generate_name()

    def _generate_password(self, length=12):
        """生成随机密码"""
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        return ''.join(random.choices(chars, k=length))

    def _generate_name(self, length=6):
        """生成随机名字"""
        first_letter = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        rest_letters = ''.join(random.choices("abcdefghijklmnopqrstuvwxyz", k=length-1))
        return first_letter + rest_letters

    def setup_email(self):
        """设置临时邮箱"""
        try:
            print(f"{Fore.CYAN}正在启动浏览器...{Style.RESET_ALL}")
            self.browser = self.browser_manager.init_browser()
            self.controller = BrowserControl(self.browser)
            
            # 打开邮箱生成器页面（第一个标签页）
            self.controller.navigate_to(self.mail_url)
            self.email_tab = self.browser  # 保存邮箱标签页
            self.controller.email_tab = self.email_tab  # 同时保存到controller
            
            # 生成新邮箱
            self.controller.generate_new_email()
            
            # 选择随机域名
            self.controller.select_email_domain()
            
            # 获取邮箱地址
            self.email_address = self.controller.copy_and_get_email()
            if self.email_address:
                print(f"{Fore.CYAN}获取到的邮箱地址: {self.email_address}{Style.RESET_ALL}")
                
                # 进入邮箱
                if self.controller.view_mailbox():
                    return True
            
            return False
            
        except Exception as e:
            print(f"{Fore.RED}发生错误: {str(e)}{Style.RESET_ALL}")
            return False

    def register_cursor(self):
        """注册 Cursor 账号"""
        signup_browser_manager = None
        try:
            print(f"\n{Fore.CYAN}{EMOJI['START']} 开始 Cursor 注册流程{Style.RESET_ALL}")
            
            # 创建新的浏览器实例用于注册
            from browser import BrowserManager
            signup_browser_manager = BrowserManager(noheader=True)
            self.signup_tab = signup_browser_manager.init_browser()
            
            # 访问注册页面
            self.signup_tab.get(self.sign_up_url)
            time.sleep(2)

            # 填写注册表单
            if self.signup_tab.ele("@name=first_name"):
                print(f"{Fore.YELLOW}{EMOJI['FORM']} 填写注册信息...{Style.RESET_ALL}")
                
                self.signup_tab.ele("@name=first_name").input(self.first_name)
                time.sleep(random.uniform(1, 2))
                
                self.signup_tab.ele("@name=last_name").input(self.last_name)
                time.sleep(random.uniform(1, 2))
                
                self.signup_tab.ele("@name=email").input(self.email_address)
                time.sleep(random.uniform(1, 2))
                
                self.signup_tab.ele("@type=submit").click()
                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} 基本信息提交完成{Style.RESET_ALL}")

            # 处理 Turnstile 验证
            self._handle_turnstile()

            # 设置密码
            if self.signup_tab.ele("@name=password"):
                print(f"{Fore.YELLOW}{EMOJI['PASSWORD']} 设置密码...{Style.RESET_ALL}")
                self.signup_tab.ele("@name=password").input(self.password)
                time.sleep(random.uniform(1, 2))
                self.signup_tab.ele("@type=submit").click()
            
            self._handle_turnstile()

            # 等待并获取验证码
            time.sleep(5)  # 等待验证码邮件

            self.browser.refresh()
            
            # 获取验证码，设置60秒超时
            verification_code = None
            max_attempts = 10  # 增加到10次尝试
            retry_interval = 5  # 每5秒重试一次
            start_time = time.time()
            timeout = 60  # 60秒超时

            print(f"{Fore.CYAN}{EMOJI['WAIT']} 开始获取验证码，将在60秒内尝试...{Style.RESET_ALL}")
            
            for attempt in range(max_attempts):
                # 检查是否超时
                if time.time() - start_time > timeout:
                    print(f"{Fore.RED}{EMOJI['ERROR']} 获取验证码超时{Style.RESET_ALL}")
                    break
                    
                verification_code = self.controller.get_verification_code()
                if verification_code:
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} 成功获取验证码: {verification_code}{Style.RESET_ALL}")
                    break
                    
                remaining_time = int(timeout - (time.time() - start_time))
                print(f"{Fore.YELLOW}{EMOJI['WAIT']} 第 {attempt + 1} 次尝试未获取到验证码，剩余时间: {remaining_time}秒{Style.RESET_ALL}")
                
                # 刷新邮箱
                self.browser.refresh()
                time.sleep(retry_interval)
            
            if verification_code:
                # 在注册页面填写验证码
                for i, digit in enumerate(verification_code):
                    self.signup_tab.ele(f"@data-index={i}").input(digit)
                    time.sleep(random.uniform(0.1, 0.3))
                
                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} 验证码填写完成{Style.RESET_ALL}")
                time.sleep(3)

                self._handle_turnstile()
                
                # 检查当前URL
                current_url = self.signup_tab.url
                if "authenticator.cursor.sh" in current_url:
                    print(f"{Fore.CYAN}{EMOJI['VERIFY']} 检测到登录页面，开始登录...{Style.RESET_ALL}")
                    
                    # 填写邮箱
                    email_input = self.signup_tab.ele('@name=email')
                    if email_input:
                        email_input.input(self.email_address)
                        time.sleep(random.uniform(1, 2))
                        
                        # 点击提交
                        submit_button = self.signup_tab.ele('@type=submit')
                        if submit_button:
                            submit_button.click()
                            time.sleep(2)
                            
                            # 处理 Turnstile 验证
                            self._handle_turnstile()
                            
                            # 填写密码
                            password_input = self.signup_tab.ele('@name=password')
                            if password_input:
                                password_input.input(self.password)
                                time.sleep(random.uniform(1, 2))
                                
                                # 点击提交
                                submit_button = self.signup_tab.ele('@type=submit')
                                if submit_button:
                                    submit_button.click()
                                    time.sleep(2)
                                    
                                    # 处理 Turnstile 验证
                                    self._handle_turnstile()
                                    
                                    # 等待跳转到设置页面
                                    max_wait = 30
                                    start_time = time.time()
                                    while time.time() - start_time < max_wait:
                                        if "cursor.com/settings" in self.signup_tab.url:
                                            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} 成功登录并跳转到设置页面{Style.RESET_ALL}")
                                            break
                                        time.sleep(1)
                
                # 获取账户信息
                result = self._get_account_info()
                
                # 关闭注册窗口
                if signup_browser_manager:
                    signup_browser_manager.quit()
                    
                return result
            else:
                print(f"{Fore.RED}{EMOJI['ERROR']} 未能在60秒内获取到验证码{Style.RESET_ALL}")
                return False

        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} 注册过程出错: {str(e)}{Style.RESET_ALL}")
            return False
        finally:
            # 确保在任何情况下都关闭注册窗口
            if signup_browser_manager:
                signup_browser_manager.quit()

    def _handle_turnstile(self):
        """处理 Turnstile 验证"""
        print(f"{Fore.YELLOW}{EMOJI['VERIFY']} 处理 Turnstile 验证...{Style.RESET_ALL}")
        
        # 设置最大等待时间（秒）
        max_wait_time = 5
        start_time = time.time()
        
        while True:
            try:
                # 检查是否超时
                if time.time() - start_time > max_wait_time:
                    print(f"{Fore.YELLOW}{EMOJI['WAIT']} 未检测到 Turnstile 验证，继续下一步...{Style.RESET_ALL}")
                    break
                    
                # 检查是否存在验证框
                challengeCheck = (
                    self.signup_tab.ele("@id=cf-turnstile", timeout=1)
                    .child()
                    .shadow_root.ele("tag:iframe")
                    .ele("tag:body")
                    .sr("tag:input")
                )

                if challengeCheck:
                    challengeCheck.click()
                    time.sleep(2)
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Turnstile 验证通过{Style.RESET_ALL}")
                    break
                    
                # 检查是否已经通过验证（检查下一步的元素是否存在）
                if self.signup_tab.ele("@name=password"):
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} 验证已通过{Style.RESET_ALL}")
                    break
                    
            except:
                # 等待短暂时间后继续检查
                time.sleep(0.5)
                continue

    def _get_account_info(self):
        """获取账户信息和 Token"""
        try:
            # 访问设置页面
            self.signup_tab.get(self.settings_url)
            time.sleep(2)
            
            # 获取账户额度信息
            usage_selector = (
                "css:div.col-span-2 > div > div > div > div > "
                "div:nth-child(1) > div.flex.items-center.justify-between.gap-2 > "
                "span.font-mono.text-sm\\/\\[0\\.875rem\\]"
            )
            usage_ele = self.signup_tab.ele(usage_selector)
            total_usage = "未知"
            if usage_ele:
                total_usage = usage_ele.text.split("/")[-1].strip()

            # 获取 Token
            print(f"{Fore.CYAN}{EMOJI['WAIT']} 开始获取 Cursor Session Token...{Style.RESET_ALL}")
            max_attempts = 30
            retry_interval = 2
            attempts = 0

            while attempts < max_attempts:
                try:
                    cookies = self.signup_tab.cookies()
                    for cookie in cookies:
                        if cookie.get("name") == "WorkosCursorSessionToken":
                            token = cookie["value"].split("%3A%3A")[1]
                            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Token 获取成功{Style.RESET_ALL}")
                            # 保存账户信息
                            self._save_account_info(token, total_usage)
                            return True

                    attempts += 1
                    if attempts < max_attempts:
                        print(
                            f"{Fore.YELLOW}{EMOJI['WAIT']} 第 {attempts} 次尝试未获取到 Token，{retry_interval}秒后重试...{Style.RESET_ALL}"
                        )
                        time.sleep(retry_interval)
                    else:
                        print(f"{Fore.RED}{EMOJI['ERROR']} 已达到最大尝试次数({max_attempts})，获取 Token 失败{Style.RESET_ALL}")

                except Exception as e:
                    print(f"{Fore.RED}{EMOJI['ERROR']} 获取 Token 失败: {str(e)}{Style.RESET_ALL}")
                    attempts += 1
                    if attempts < max_attempts:
                        print(f"{Fore.YELLOW}{EMOJI['WAIT']} 将在 {retry_interval} 秒后重试...{Style.RESET_ALL}")
                        time.sleep(retry_interval)

            return False

        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} 获取账户信息失败: {str(e)}{Style.RESET_ALL}")
            return False

    def _save_account_info(self, token, total_usage):
        """保存账户信息到文件"""
        try:
            # 先更新认证信息
            print(f"{Fore.CYAN}{EMOJI['KEY']} 正在更新 Cursor 认证信息...{Style.RESET_ALL}")
            if update_cursor_auth(email=self.email_address, access_token=token, refresh_token=token):
                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Cursor 认证信息更新成功{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}{EMOJI['ERROR']} Cursor 认证信息更新失败{Style.RESET_ALL}")

            # 重置机器ID
            print(f"{Fore.CYAN}{EMOJI['UPDATE']} 正在重置机器ID...{Style.RESET_ALL}")
            MachineIDResetter().reset_machine_ids()
            
            # 保存账户信息到文件
            with open('cursor_accounts.txt', 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*50}\n")
                f.write(f"Email: {self.email_address}\n")
                f.write(f"Password: {self.password}\n")
                f.write(f"Token: {token}\n")
                f.write(f"Usage Limit: {total_usage}\n")
                f.write(f"{'='*50}\n")
                
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} 账户信息已保存到 cursor_accounts.txt{Style.RESET_ALL}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} 保存账户信息失败: {str(e)}{Style.RESET_ALL}")
            return False

    def start(self):
        """启动注册流程"""
        try:
            if self.setup_email():
                if self.register_cursor():
                    print(f"\n{Fore.GREEN}{EMOJI['DONE']} Cursor 注册完成！{Style.RESET_ALL}")
                    return True
            return False
        finally:
            if self.browser_manager:
                self.browser_manager.quit()



def update_cursor_auth(email=None, access_token=None, refresh_token=None):
    """
    更新Cursor的认证信息的便捷函数
    """
    auth_manager = CursorAuth()
    return auth_manager.update_auth(email, access_token, refresh_token)

def main():
    registration = CursorRegistration()
    registration.start()

if __name__ == "__main__":
    main() 