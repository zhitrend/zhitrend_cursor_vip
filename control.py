import time
from colorama import Fore, Style
import random
import os

class BrowserControl:
    def __init__(self, browser):
        self.browser = browser
        self.sign_up_url = "https://authenticator.cursor.sh/sign-up"
        self.current_tab = None  # 当前标签页
        self.signup_tab = None   # 注册标签页
        self.email_tab = None    # 邮箱标签页

    def create_new_tab(self):
        """创建新标签页"""
        try:
            # 保存当前标签页
            self.current_tab = self.browser
            
            # 创建新的浏览器实例
            from browser import BrowserManager
            browser_manager = BrowserManager()
            new_browser = browser_manager.init_browser()
            
            # 保存新标签页
            self.signup_tab = new_browser
            
            print(f"{Fore.GREEN}成功创建新窗口{Style.RESET_ALL}")
            return new_browser
        except Exception as e:
            print(f"{Fore.RED}创建新窗口时发生错误: {str(e)}{Style.RESET_ALL}")
            return None

    def switch_to_tab(self, browser):
        """切换到指定浏览器窗口"""
        try:
            self.browser = browser
            print(f"{Fore.GREEN}成功切换窗口{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}切换窗口时发生错误: {str(e)}{Style.RESET_ALL}")
            return False

    def get_current_tab(self):
        """获取当前标签页"""
        return self.browser

    def generate_new_email(self):
        """点击新的按钮生成新邮箱"""
        try:
            print(f"{Fore.CYAN}点击生成新邮箱...{Style.RESET_ALL}")
            new_button = self.browser.ele('xpath://button[contains(@class, "egenbut")]')
            if new_button:
                new_button.click()
                time.sleep(1)  # 等待生成
                print(f"{Fore.GREEN}成功生成新邮箱{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}未找到生成按钮{Style.RESET_ALL}")
                return False
        except Exception as e:
            print(f"{Fore.RED}生成新邮箱时发生错误: {str(e)}{Style.RESET_ALL}")
            return False

    def select_email_domain(self, domain_index=None):
        """选择邮箱域名，如果不指定index则随机选择"""
        try:
            print(f"{Fore.CYAN}选择邮箱域名...{Style.RESET_ALL}")
            # 找到下拉框
            select_element = self.browser.ele('xpath://select[@id="seldom"]')
            if select_element:
                # 获取所有选项，包括两个 optgroup 下的所有 option
                all_options = []
                
                # 获取 "新的" 组下的选项
                new_options = self.browser.eles('xpath://select[@id="seldom"]/optgroup[@label="-- 新的 --"]/option')
                all_options.extend(new_options)
                
                # 获取 "其他" 组下的选项
                other_options = self.browser.eles('xpath://select[@id="seldom"]/optgroup[@label="-- 其他 --"]/option')
                all_options.extend(other_options)
                
                if all_options:
                    # 如果没有指定索引，随机选择一个
                    if domain_index is None:
                        domain_index = random.randint(0, len(all_options) - 1)
                    
                    if domain_index < len(all_options):
                        # 获取选中选项的文本
                        selected_domain = all_options[domain_index].text
                        print(f"{Fore.CYAN}选择域名: {selected_domain}{Style.RESET_ALL}")
                        
                        # 点击选择
                        all_options[domain_index].click()
                        time.sleep(1)
                        print(f"{Fore.GREEN}成功选择邮箱域名{Style.RESET_ALL}")
                        return True
                    
                print(f"{Fore.RED}未找到可用的域名选项，总共有 {len(all_options)} 个选项{Style.RESET_ALL}")
                return False
            else:
                print(f"{Fore.RED}未找到域名选择框{Style.RESET_ALL}")
                return False
        except Exception as e:
            print(f"{Fore.RED}选择邮箱域名时发生错误: {str(e)}{Style.RESET_ALL}")
            return False

    def wait_for_page_load(self, seconds=2):
        """等待页面加载"""
        time.sleep(seconds)

    def navigate_to(self, url):
        """导航到指定URL"""
        try:
            print(f"{Fore.CYAN}正在访问 {url}...{Style.RESET_ALL}")
            self.browser.get(url)
            self.wait_for_page_load()
            return True
        except Exception as e:
            print(f"{Fore.RED}访问 {url} 时发生错误: {str(e)}{Style.RESET_ALL}")
            return False 

    def copy_and_get_email(self):
        """获取邮箱地址"""
        try:
            print(f"{Fore.CYAN}获取邮箱信息...{Style.RESET_ALL}")
            
            # 等待元素加载
            time.sleep(1)
            
            # 获取邮箱名称
            try:
                email_div = self.browser.ele('xpath://div[@class="segen"]//div[contains(@style, "color: #e5e5e5")]')
                if email_div:
                    email_name = email_div.text.split()[0]
                    print(f"{Fore.CYAN}找到邮箱名称: {email_name}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}无法找到邮箱名称元素{Style.RESET_ALL}")
                    return None
            except Exception as e:
                print(f"{Fore.RED}获取邮箱名称时出错: {str(e)}{Style.RESET_ALL}")
                return None
            
            # 直接使用上一步选择的域名
            try:
                domain = self.browser.ele('xpath://select[@id="seldom"]').value
                if not domain:  # 如果获取不到value，尝试获取选中的选项文本
                    selected_option = self.browser.ele('xpath://select[@id="seldom"]/option[1]')
                    domain = selected_option.text if selected_option else "@yopmail.com"  # 使用默认域名作为后备
            except:
                domain = "@yopmail.com"  # 如果出错，使用默认域名
            
            # 组合完整邮箱地址
            full_email = f"{email_name}{domain}"
            print(f"{Fore.GREEN}完整邮箱地址: {full_email}{Style.RESET_ALL}")
            return full_email
            
        except Exception as e:
            print(f"{Fore.RED}获取邮箱地址时发生错误: {str(e)}{Style.RESET_ALL}")
            return None 

    def view_mailbox(self):
        """点击查看邮箱按钮"""
        try:
            print(f"{Fore.CYAN}正在进入邮箱...{Style.RESET_ALL}")
            view_button = self.browser.ele('xpath://button[contains(@class, "egenbut") and contains(.//span, "查看邮箱")]')
            if view_button:
                view_button.click()
                time.sleep(2)  # 等待页面加载
                print(f"{Fore.GREEN}成功进入邮箱{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}未找到查看邮箱按钮{Style.RESET_ALL}")
                return False
        except Exception as e:
            print(f"{Fore.RED}进入邮箱时发生错误: {str(e)}{Style.RESET_ALL}")
            return False 

    def refresh_mailbox(self):
        """刷新邮箱获取最新信息"""
        try:
            print(f"{Fore.CYAN}正在刷新邮箱...{Style.RESET_ALL}")
            refresh_button = self.browser.ele('xpath://button[@id="refresh"]')
            if refresh_button:
                refresh_button.click()
                time.sleep(2)  # 等待刷新完成
                print(f"{Fore.GREEN}邮箱刷新成功{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}未找到刷新按钮{Style.RESET_ALL}")
                return False
        except Exception as e:
            print(f"{Fore.RED}刷新邮箱时发生错误: {str(e)}{Style.RESET_ALL}")
            return False 

    def check_and_click_recaptcha(self):
        """检查并点击验证码复选框"""
        try:
            # 使用环境变量或配置文件中预设的坐标
            click_x = int(os.getenv('RECAPTCHA_X', '100'))  # 默认值100
            click_y = int(os.getenv('RECAPTCHA_Y', '100'))  # 默认值100
            
            print(f"{Fore.CYAN}使用预设坐标点击: x={click_x}, y={click_y}{Style.RESET_ALL}")
            
            # 直接点击预设坐标
            self.browser.page.mouse.click(click_x, click_y)
            print(f"{Fore.GREEN}已点击 reCAPTCHA 位置{Style.RESET_ALL}")
            time.sleep(1)
            return True
            
        except Exception as e:
            print(f"{Fore.YELLOW}点击 reCAPTCHA 失败: {str(e)}{Style.RESET_ALL}")
            return False 

    def get_verification_code(self):
        """从邮件中获取验证码"""
        try:
            # 查找包含验证码的div，使用更精确的XPath
            code_div = self.browser.ele('xpath://div[contains(@style, "font-family:-apple-system") and contains(@style, "font-size: 28px") and contains(@style, "letter-spacing: 2px") and contains(@style, "color: rgba(32, 32, 32, 1)")]')
            if code_div:
                verification_code = code_div.text.strip()
                if verification_code.isdigit() and len(verification_code) == 6:
                    print(f"{Fore.GREEN}找到验证码: {verification_code}{Style.RESET_ALL}")
                    return verification_code
                else:
                    print(f"{Fore.RED}验证码格式不正确: {verification_code}{Style.RESET_ALL}")
                    return None
            else:
                # 尝试备用XPath
                code_div = self.browser.ele('xpath://div[contains(@style, "font-size: 28px") and contains(@style, "letter-spacing: 2px") and contains(@style, "color: rgba(32, 32, 32, 1)")]')
                if code_div:
                    verification_code = code_div.text.strip()
                    if verification_code.isdigit() and len(verification_code) == 6:
                        print(f"{Fore.GREEN}找到验证码: {verification_code}{Style.RESET_ALL}")
                        return verification_code
                print(f"{Fore.RED}未找到验证码{Style.RESET_ALL}")
                return None
        except Exception as e:
            print(f"{Fore.RED}获取验证码时发生错误: {str(e)}{Style.RESET_ALL}")
            return None

    def fill_verification_code(self, code):
        """填写验证码"""
        try:
            if not code or len(code) != 6:
                print(f"{Fore.RED}验证码格式不正确{Style.RESET_ALL}")
                return False

            print(f"{Fore.CYAN}正在填写验证码...{Style.RESET_ALL}")
            
            # 记住当前标签页（邮箱页面）
            email_tab = self.browser
            
            # 切换回注册页面标签
            self.switch_to_tab(self.signup_tab)
            time.sleep(1)
            
            # 输入验证码
            for digit in code:
                self.browser.actions.input(digit)
                time.sleep(random.uniform(0.1, 0.3))
            
            print(f"{Fore.GREEN}验证码填写完成{Style.RESET_ALL}")
            
            # 等待页面加载和登录完成
            print(f"{Fore.CYAN}等待登录完成...{Style.RESET_ALL}")
            time.sleep(5)
            
            # 先访问登录页面确保登录状态
            login_url = "https://authenticator.cursor.sh"
            self.browser.get(login_url)
            time.sleep(3)  # 增加等待时间
            
            # 获取cookies（第一次尝试）
            token = self.get_cursor_session_token()
            if not token:
                print(f"{Fore.YELLOW}首次获取token失败，等待后重试...{Style.RESET_ALL}")
                time.sleep(3)
                token = self.get_cursor_session_token()
            
            if token:
                self.save_token_to_file(token)
                
                # 获取到token后再访问设置页面
                settings_url = "https://www.cursor.com/settings"
                print(f"{Fore.CYAN}正在访问设置页面获取账户信息...{Style.RESET_ALL}")
                self.browser.get(settings_url)
                time.sleep(2)
                
                # 获取账户额度信息
                try:
                    usage_selector = (
                        "css:div.col-span-2 > div > div > div > div > "
                        "div:nth-child(1) > div.flex.items-center.justify-between.gap-2 > "
                        "span.font-mono.text-sm\\/\\[0\\.875rem\\]"
                    )
                    usage_ele = self.browser.ele(usage_selector)
                    if usage_ele:
                        usage_info = usage_ele.text
                        total_usage = usage_info.split("/")[-1].strip()
                        print(f"{Fore.GREEN}账户可用额度上限: {total_usage}{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}获取账户额度信息失败: {str(e)}{Style.RESET_ALL}")
            
            # 切换回邮箱页面
            self.switch_to_tab(email_tab)
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}填写验证码时发生错误: {str(e)}{Style.RESET_ALL}")
            return False 

    def check_and_click_turnstile(self):
        """检查并点击 Turnstile 验证框"""
        try:
            # 等待验证框出现
            time.sleep(1)
            
            # 查找验证框
            verify_checkbox = self.browser.ele('xpath://label[contains(@class, "cb-lb")]//input[@type="checkbox"]')
            if verify_checkbox:
                print(f"{Fore.CYAN}找到 Turnstile 验证框，尝试点击...{Style.RESET_ALL}")
                verify_checkbox.click()
                time.sleep(2)  # 等待验证完成
                print(f"{Fore.GREEN}已点击 Turnstile 验证框{Style.RESET_ALL}")
                return True
            return False
        except Exception as e:
            print(f"{Fore.YELLOW}未找到 Turnstile 验证框或点击失败: {str(e)}{Style.RESET_ALL}")
            return False 

    def get_cursor_session_token(self, max_attempts=3, retry_interval=2):
        """获取Cursor会话token"""
        print(f"{Fore.CYAN}开始获取cookie...{Style.RESET_ALL}")
        attempts = 0

        while attempts < max_attempts:
            try:
                # 直接从浏览器对象获取cookies
                all_cookies = self.browser.get_cookies()
                
                # 遍历查找目标cookie
                for cookie in all_cookies:
                    if cookie.get("name") == "WorkosCursorSessionToken":
                        token = cookie["value"].split("%3A%3A")[1]
                        print(f"{Fore.GREEN}成功获取CursorSessionToken: {token}{Style.RESET_ALL}")
                        return token

                attempts += 1
                if attempts < max_attempts:
                    print(f"{Fore.YELLOW}第 {attempts} 次尝试未获取到CursorSessionToken，{retry_interval}秒后重试...{Style.RESET_ALL}")
                    time.sleep(retry_interval)
                else:
                    print(f"{Fore.RED}已达到最大尝试次数({max_attempts})，获取CursorSessionToken失败{Style.RESET_ALL}")

            except Exception as e:
                print(f"{Fore.RED}获取cookie失败: {str(e)}{Style.RESET_ALL}")
                attempts += 1
                if attempts < max_attempts:
                    print(f"{Fore.YELLOW}将在 {retry_interval} 秒后重试...{Style.RESET_ALL}")
                    time.sleep(retry_interval)

        return None

    def save_token_to_file(self, token):
        """保存token到文件"""
        try:
            with open('cursor_tokens.txt', 'a', encoding='utf-8') as f:
                f.write(f"Token: {token}\n")
                f.write("-" * 50 + "\n")
            print(f"{Fore.GREEN}Token已保存到 cursor_tokens.txt{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}保存Token时发生错误: {str(e)}{Style.RESET_ALL}") 