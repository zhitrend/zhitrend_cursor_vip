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

# 定义emoji常量
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
    'MAIL': '📧',
    'KEY': '🔐',
    'UPDATE': '🔄',
    'INFO': 'ℹ️'
}

class CursorRegistration:
    def __init__(self, translator=None):
        self.translator = translator
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
        """Generate Random Password"""
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        return ''.join(random.choices(chars, k=length))

    def _generate_name(self, length=6):
        """Generate Random Name"""
        first_letter = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        rest_letters = ''.join(random.choices("abcdefghijklmnopqrstuvwxyz", k=length-1))
        return first_letter + rest_letters

    def setup_email(self):
        """设置邮箱"""
        try:
            print(f"{Fore.CYAN}{EMOJI['START']} {self.translator.get('register.browser_start')}...{Style.RESET_ALL}")
            self.browser = self.browser_manager.init_browser()
            self.controller = BrowserControl(self.browser, self.translator)
            
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
                print(f"{EMOJI['MAIL']}{Fore.CYAN} {self.translator.get('register.get_email_address')}: {self.email_address}{Style.RESET_ALL}")
                
                # 进入邮箱
                if self.controller.view_mailbox():
                    return True
            
            return False
            
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('register.setup_error', error=str(e))}{Style.RESET_ALL}")
            return False

    def register_cursor(self):
        """注册 Cursor"""
        signup_browser_manager = None
        try:
            print(f"{Fore.CYAN}{EMOJI['START']} {self.translator.get('register.register_start')}...{Style.RESET_ALL}")
            
            # 创建新的浏览器实例用于注册
            from browser import BrowserManager
            signup_browser_manager = BrowserManager(noheader=True)
            self.signup_tab = signup_browser_manager.init_browser()
            
            # 访问注册页面
            self.signup_tab.get(self.sign_up_url)
            time.sleep(2)

            # 填写注册表单
            if self.signup_tab.ele("@name=first_name"):
                print(f"{Fore.CYAN}{EMOJI['FORM']} {self.translator.get('register.filling_form')}...{Style.RESET_ALL}")
                
                self.signup_tab.ele("@name=first_name").input(self.first_name)
                time.sleep(random.uniform(1, 2))
                
                self.signup_tab.ele("@name=last_name").input(self.last_name)
                time.sleep(random.uniform(1, 2))
                
                self.signup_tab.ele("@name=email").input(self.email_address)
                time.sleep(random.uniform(1, 2))
                
                self.signup_tab.ele("@type=submit").click()
                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('register.basic_info_submitted')}...{Style.RESET_ALL}")

            # 处理 Turnstile 验证
            self._handle_turnstile()

            # 设置密码
            if self.signup_tab.ele("@name=password"):
                print(f"{Fore.CYAN}{EMOJI['PASSWORD']} {self.translator.get('register.set_password')}...{Style.RESET_ALL}")
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

            print(f"{Fore.CYAN}{EMOJI['WAIT']} {self.translator.get('register.start_getting_verification_code')}...{Style.RESET_ALL}")
            
            for attempt in range(max_attempts):
                # 检查是否超时
                if time.time() - start_time > timeout:
                    print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('register.get_verification_code_timeout')}...{Style.RESET_ALL}")
                    break
                    
                verification_code = self.controller.get_verification_code()
                if verification_code:
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('register.get_verification_code_success')}: {verification_code}{Style.RESET_ALL}")
                    break
                    
                remaining_time = int(timeout - (time.time() - start_time))
                print(f"{Fore.YELLOW}{EMOJI['WAIT']} {self.translator.get('register.try_get_verification_code', attempt=attempt + 1, remaining_time=remaining_time)}...{Style.RESET_ALL}")
                
                # 刷新邮箱
                self.browser.refresh()
                time.sleep(retry_interval)
            
            if verification_code:
                # 在注册页面填写验证码
                for i, digit in enumerate(verification_code):
                    self.signup_tab.ele(f"@data-index={i}").input(digit)
                    time.sleep(random.uniform(0.1, 0.3))
                
                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('register.verification_code_filled')}...{Style.RESET_ALL}")
                time.sleep(3)

                self._handle_turnstile()
                
                # 检查当前URL
                current_url = self.signup_tab.url
                if "authenticator.cursor.sh" in current_url:
                    print(f"{Fore.CYAN}{EMOJI['VERIFY']} {self.translator.get('register.detect_login_page')}...{Style.RESET_ALL}")
                    
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
                                            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('register.login_success_and_jump_to_settings_page')}...{Style.RESET_ALL}")
                                            break
                                        time.sleep(1)
                
                # 获取账户信息
                result = self._get_account_info()
                
                # 关闭注册窗口
                if signup_browser_manager:
                    signup_browser_manager.quit()
                    
                return result
            else:
                print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('register.get_verification_code_timeout')}...{Style.RESET_ALL}")
                return False

        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('register.register_process_error', error=str(e))}{Style.RESET_ALL}")
            return False
        finally:
            # 确保在任何情况下都关闭注册窗口
            if signup_browser_manager:
                signup_browser_manager.quit()

    def _handle_turnstile(self):
        """处理 Turnstile 验证"""
        print(f"{Fore.YELLOW}{EMOJI['VERIFY']} {self.translator.get('register.handle_turnstile')}...{Style.RESET_ALL}")
        
        # 设置最大等待时间（秒）
        max_wait_time = 10  # 增加等待时间
        start_time = time.time()
        
        while True:
            try:
                # 检查是否超时
                if time.time() - start_time > max_wait_time:
                    print(f"{Fore.YELLOW}{EMOJI['WAIT']} {self.translator.get('register.no_turnstile')}...{Style.RESET_ALL}")
                    time.sleep(2)
                    break
                    
                try:
                    challengeCheck = (
                        self.signup_tab.ele("@id=cf-turnstile", timeout=1)
                        .child()
                        .shadow_root.ele("tag:iframe")
                        .ele("tag:body")
                        .sr("tag:input")
                    )

                    if challengeCheck:
                        challengeCheck.click()
                        time.sleep(3)
                        print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('register.turnstile_passed')}{Style.RESET_ALL}")
                        time.sleep(2)
                        break
                except:
                    pass
                    
                try:
                    if (self.signup_tab.ele("@name=password", timeout=0.5) or 
                        self.signup_tab.ele("@name=email", timeout=0.5) or
                        self.signup_tab.ele("@data-index=0", timeout=0.5)):
                        print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('register.turnstile_passed')}{Style.RESET_ALL}")
                        time.sleep(2)
                        break
                except:
                    pass
                    
                time.sleep(1)
                
            except Exception as e:
                print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('register.error', error=str(e))}{Style.RESET_ALL}")
                time.sleep(2)
                break

        time.sleep(2)

    def _get_account_info(self):
        """获取账户信息和 Token"""
        try:
            self.signup_tab.get(self.settings_url)
            time.sleep(2)
            
            usage_selector = (
                "css:div.col-span-2 > div > div > div > div > "
                "div:nth-child(1) > div.flex.items-center.justify-between.gap-2 > "
                "span.font-mono.text-sm\\/\\[0\\.875rem\\]"
            )
            usage_ele = self.signup_tab.ele(usage_selector)
            total_usage = "未知"
            if usage_ele:
                total_usage = usage_ele.text.split("/")[-1].strip()

            print(f"{Fore.CYAN}{EMOJI['WAIT']} {self.translator.get('register.get_token')}...{Style.RESET_ALL}")
            max_attempts = 30
            retry_interval = 2
            attempts = 0

            while attempts < max_attempts:
                try:
                    cookies = self.signup_tab.cookies()
                    for cookie in cookies:
                        if cookie.get("name") == "WorkosCursorSessionToken":
                            token = cookie["value"].split("%3A%3A")[1]
                            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('register.token_success')}{Style.RESET_ALL}")
                            self._save_account_info(token, total_usage)
                            return True

                    attempts += 1
                    if attempts < max_attempts:
                        print(f"{Fore.YELLOW}{EMOJI['WAIT']} {self.translator.get('register.token_attempt', attempt=attempts, time=retry_interval)}{Style.RESET_ALL}")
                        time.sleep(retry_interval)
                    else:
                        print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('register.token_max_attempts', max=max_attempts)}{Style.RESET_ALL}")

                except Exception as e:
                    print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('register.token_failed', error=str(e))}{Style.RESET_ALL}")
                    attempts += 1
                    if attempts < max_attempts:
                        print(f"{Fore.YELLOW}{EMOJI['WAIT']} {self.translator.get('register.token_attempt', attempt=attempts, time=retry_interval)}{Style.RESET_ALL}")
                        time.sleep(retry_interval)

            return False

        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('register.account_error', error=str(e))}{Style.RESET_ALL}")
            return False

    def _save_account_info(self, token, total_usage):
        """保存账户信息到文件"""
        try:
            # 先更新认证信息
            print(f"{Fore.CYAN}{EMOJI['KEY']} {self.translator.get('register.update_cursor_auth_info')}...{Style.RESET_ALL}")
            if self.update_cursor_auth(email=self.email_address, access_token=token, refresh_token=token):
                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('register.cursor_auth_info_updated')}...{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('register.cursor_auth_info_update_failed')}...{Style.RESET_ALL}")

            # 重置机器ID
            print(f"{Fore.CYAN}{EMOJI['UPDATE']} {self.translator.get('register.reset_machine_id')}...{Style.RESET_ALL}")
            resetter = MachineIDResetter(self.translator)  # 创建实例时传入translator
            if not resetter.reset_machine_ids():  # 直接调用reset_machine_ids方法
                raise Exception("Failed to reset machine ID")
            
            # 保存账户信息到文件
            with open('cursor_accounts.txt', 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*50}\n")
                f.write(f"Email: {self.email_address}\n")
                f.write(f"Password: {self.password}\n")
                f.write(f"Token: {token}\n")
                f.write(f"Usage Limit: {total_usage}\n")
                f.write(f"{'='*50}\n")
                
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('register.account_info_saved')}...{Style.RESET_ALL}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('register.save_account_info_failed', error=str(e))}{Style.RESET_ALL}")
            return False

    def start(self):
        """启动注册流程"""
        try:
            if self.setup_email():
                if self.register_cursor():
                    print(f"\n{Fore.GREEN}{EMOJI['DONE']} {self.translator.get('register.cursor_registration_completed')}...{Style.RESET_ALL}")
                    return True
            return False
        finally:
            if self.browser_manager:
                self.browser_manager.quit()

    def update_cursor_auth(self, email=None, access_token=None, refresh_token=None):
        """更新Cursor的认证信息的便捷函数"""
        auth_manager = CursorAuth(translator=self.translator)
        return auth_manager.update_auth(email, access_token, refresh_token)

def main(translator=None):
    """Main function to be called from main.py"""
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{EMOJI['START']} {translator.get('register.title')}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

    registration = CursorRegistration(translator)
    registration.start()

    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    input(f"{EMOJI['INFO']} {translator.get('register.press_enter')}...")

if __name__ == "__main__":
    from main import translator as main_translator
    main(main_translator) 