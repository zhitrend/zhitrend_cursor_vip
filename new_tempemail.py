from DrissionPage import ChromiumPage, ChromiumOptions
import time
import os
import sys
from colorama import Fore, Style, init
import requests
import random
import string
from utils import get_random_wait_time

# Initialize colorama
init()

class NewTempEmail:
    def __init__(self, translator=None):
        self.translator = translator
        self.page = None
        self.setup_browser()
        
    def get_blocked_domains(self):
        """Get blocked domains list"""
        try:
            block_url = "https://raw.githubusercontent.com/yeongpin/cursor-free-vip/main/block_domain.txt"
            response = requests.get(block_url, timeout=5)
            if response.status_code == 200:
                # Split text and remove empty lines
                domains = [line.strip() for line in response.text.split('\n') if line.strip()]
                if self.translator:
                    print(f"{Fore.CYAN}ℹ️  {self.translator.get('email.blocked_domains_loaded', count=len(domains))}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.CYAN}ℹ️ 已加载 {len(domains)} 个被屏蔽的域名{Style.RESET_ALL}")
                return domains
            return self._load_local_blocked_domains()
        except Exception as e:
            if self.translator:
                print(f"{Fore.YELLOW}⚠️ {self.translator.get('email.blocked_domains_error', error=str(e))}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠️ 获取被屏蔽域名列表失败: {str(e)}{Style.RESET_ALL}")
            return self._load_local_blocked_domains()
            
    def _load_local_blocked_domains(self):
        """Load blocked domains from local file as fallback"""
        try:
            local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "block_domain.txt")
            if os.path.exists(local_path):
                with open(local_path, 'r', encoding='utf-8') as f:
                    domains = [line.strip() for line in f.readlines() if line.strip()]
                if self.translator:
                    print(f"{Fore.CYAN}ℹ️  {self.translator.get('email.local_blocked_domains_loaded', count=len(domains))}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.CYAN}ℹ️ 已从本地加载 {len(domains)} 个被屏蔽的域名{Style.RESET_ALL}")
                return domains
            else:
                if self.translator:
                    print(f"{Fore.YELLOW}⚠️ {self.translator.get('email.local_blocked_domains_not_found')}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}⚠️ 本地被屏蔽域名文件不存在{Style.RESET_ALL}")
                return []
        except Exception as e:
            if self.translator:
                print(f"{Fore.YELLOW}⚠️ {self.translator.get('email.local_blocked_domains_error', error=str(e))}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠️ 读取本地被屏蔽域名文件失败: {str(e)}{Style.RESET_ALL}")
            return []
    
    def exclude_blocked_domains(self, domains):
        """Exclude blocked domains"""
        if not self.blocked_domains:
            return domains
            
        filtered_domains = []
        for domain in domains:
            if domain['domain'] not in self.blocked_domains:
                filtered_domains.append(domain)
                
        excluded_count = len(domains) - len(filtered_domains)
        if excluded_count > 0:
            if self.translator:
                print(f"{Fore.YELLOW}⚠️ {self.translator.get('email.domains_excluded', domains=excluded_count)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠️ 已排除 {excluded_count} 个被屏蔽的域名{Style.RESET_ALL}")
                
        return filtered_domains
        
        
    def get_extension_block(self):
        """获取插件路径"""
        root_dir = os.getcwd()
        extension_path = os.path.join(root_dir, "PBlock")
        
        if hasattr(sys, "_MEIPASS"):
            extension_path = os.path.join(sys._MEIPASS, "PBlock")

        if not os.path.exists(extension_path):
            raise FileNotFoundError(f"插件不存在: {extension_path}")

        return extension_path
        
    def setup_browser(self):
        """设置浏览器"""
        try:
            if self.translator:
                print(f"{Fore.CYAN}ℹ️ {self.translator.get('email.starting_browser')}{Style.RESET_ALL}")
            else:
                print(f"{Fore.CYAN}ℹ️ 正在启动浏览器...{Style.RESET_ALL}")
            
            # 创建浏览器选项
            co = ChromiumOptions()
            co.set_argument("--headless=new")
            
            co.auto_port()  # 自动设置端口
            
            # 加载 uBlock 插件
            try:
                extension_path = self.get_extension_block()
                co.set_argument("--allow-extensions-in-incognito")
                co.add_extension(extension_path)
            except Exception as e:
                if self.translator:
                    print(f"{Fore.YELLOW}⚠️ {self.translator.get('email.extension_load_error')}: {str(e)}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}⚠️ 加载插件失败: {str(e)}{Style.RESET_ALL}")
            
            self.page = ChromiumPage(co)
            return True
        except Exception as e:
            if self.translator:
                print(f"{Fore.RED}❌ {self.translator.get('email.browser_start_error')}: {str(e)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ 启动浏览器失败: {str(e)}{Style.RESET_ALL}")
            return False
            
    def create_email(self):
        """创建临时邮箱"""
        try:
            if self.translator:
                print(f"{Fore.CYAN}ℹ️ {self.translator.get('email.visiting_site')}{Style.RESET_ALL}")
            else:
                print(f"{Fore.CYAN}ℹ️ 正在访问 smailpro.com...{Style.RESET_ALL}")
            
            # 加载被屏蔽域名列表
            self.blocked_domains = self.get_blocked_domains()
            
            # Instead of using the default email generation, let's create a custom one
            # First try creating a custom email with legitimate-looking patterns
            try:
                legitimate_email = self.create_legitimate_looking_email()
                if legitimate_email:
                    return legitimate_email
            except Exception as e:
                if self.translator:
                    print(f"{Fore.YELLOW}⚠️ {self.translator.get('email.custom_email_error')}: {str(e)}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}⚠️ 创建自定义邮箱失败: {str(e)}, 尝试使用默认方式{Style.RESET_ALL}")
            
            # Fallback to standard email generation if custom fails
            # 访问网站
            self.page.get("https://smailpro.com/")
            time.sleep(2)
            
            # 点击创建邮箱按钮
            create_button = self.page.ele('xpath://button[@title="Create temporary email"]')
            if create_button:
                create_button.click()
                time.sleep(1)
                
                # 点击弹窗中的 Create 按钮
                modal_create_button = self.page.ele('xpath://button[contains(text(), "Create")]')
                if modal_create_button:
                    modal_create_button.click()
                    time.sleep(2)
                    
                    # 获取邮箱地址 - 修改选择器
                    email_div = self.page.ele('xpath://div[@class="text-base sm:text-lg md:text-xl text-gray-700"]')
                    if email_div:
                        email = email_div.text.strip()
                        if '@' in email:  # 验证是否是有效的邮箱地址
                            # 检查域名是否被屏蔽
                            domain = email.split('@')[1]
                            if self.blocked_domains and domain in self.blocked_domains:
                                if self.translator:
                                    print(f"{Fore.YELLOW}⚠️ {self.translator.get('email.domain_blocked')}: {domain}{Style.RESET_ALL}")
                                else:
                                    print(f"{Fore.YELLOW}⚠️ 域名已被屏蔽: {domain}，尝试重新创建邮箱{Style.RESET_ALL}")
                                # 重新创建邮箱
                                return self.create_email()
                            
                            if self.translator:
                                print(f"{Fore.GREEN}✅ {self.translator.get('email.create_success')}: {email}{Style.RESET_ALL}")
                            else:
                                print(f"{Fore.GREEN}✅ 创建邮箱成功: {email}{Style.RESET_ALL}")
                            return email
            if self.translator:
                print(f"{Fore.RED}❌ {self.translator.get('email.create_failed')}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ 创建邮箱失败{Style.RESET_ALL}")
            return None
            
        except Exception as e:
            if self.translator:
                print(f"{Fore.RED}❌ {self.translator.get('email.create_error')}: {str(e)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ 创建邮箱出错: {str(e)}{Style.RESET_ALL}")
            return None
            
    def create_legitimate_looking_email(self):
        """Create a legitimate-looking email address using a service like mailforspam.com or mail.tm"""
        try:
            # List of services to try in order of preference
            services = [
                self.try_tempmail,        # Try temp-mail.org (highly rated)
                self.try_10minutemail,    # Try 10minutemail.com (looks legitimate)
                self.try_emailondeck,     # Try EmailOnDeck (professional looking)
                self.try_yopmail,         # Try YOPmail (allows custom domains)
                self.try_throwawaymail,   # Try ThrowAwayMail (48 hour lifespan)
                self.try_mailforspam,     # Try mailforspam.com (current implementation)
                self.try_mailtm,          # Try mail.tm (current implementation)
                self.try_tempmail_plus    # Try tempmail.plus (current implementation)
            ]
            
            # Try each service until one works
            for service in services:
                try:
                    if self.translator:
                        print(f"{Fore.CYAN}ℹ️ {self.translator.get('email.trying_provider', provider=service.__name__.replace('try_', ''))}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.CYAN}ℹ️ 尝试使用 {service.__name__.replace('try_', '')} 创建邮箱...{Style.RESET_ALL}")
                    
                    email = service()
                    if email and '@' in email:
                        # Check domain against blocked list
                        domain = email.split('@')[1]
                        if self.blocked_domains and domain in self.blocked_domains:
                            if self.translator:
                                print(f"{Fore.YELLOW}⚠️ {self.translator.get('email.domain_blocked')}: {domain}{Style.RESET_ALL}")
                            else:
                                print(f"{Fore.YELLOW}⚠️ 域名已被屏蔽: {domain}，尝试另一个服务{Style.RESET_ALL}")
                            continue
                        
                        # Log success
                        if self.translator:
                            print(f"{Fore.GREEN}✅ {self.translator.get('email.create_success')}: {email}{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.GREEN}✅ 创建邮箱成功: {email}{Style.RESET_ALL}")
                        return email
                except Exception as e:
                    if self.translator:
                        print(f"{Fore.YELLOW}⚠️ {service.__name__} failed: {str(e)}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}⚠️ {service.__name__} 失败: {str(e)}{Style.RESET_ALL}")
            
            return None
        except Exception as e:
            if self.translator:
                print(f"{Fore.YELLOW}⚠️ {self.translator.get('email.legitimate_email_error')}: {str(e)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠️ 创建可信邮箱失败: {str(e)}{Style.RESET_ALL}")
            return None
    
    def generate_realistic_username(self):
        """Generate a realistic-looking email username that appears legitimate"""
        # First names for more realistic looking usernames
        first_names = [
            "john", "sara", "michael", "emma", "david", "jennifer", "robert", "lisa", "william", "emily",
            "james", "olivia", "benjamin", "sophia", "daniel", "ava", "matthew", "mia", "andrew", "charlotte",
            "joseph", "amelia", "christopher", "harper", "ryan", "evelyn", "nicholas", "abigail", "tyler", "ella",
            "alex", "grace", "nathan", "zoe", "ethan", "hannah", "jason", "lily", "kevin", "natalie"
        ]
        
        # Last names for more realistic looking usernames
        last_names = [
            "smith", "johnson", "williams", "brown", "jones", "miller", "davis", "garcia", "wilson", "martinez",
            "anderson", "taylor", "thomas", "moore", "jackson", "martin", "lee", "perez", "thompson", "white",
            "harris", "sanchez", "clark", "ramirez", "lewis", "robinson", "walker", "young", "allen", "king",
            "wright", "scott", "green", "baker", "adams", "nelson", "hill", "rivera", "campbell", "mitchell"
        ]
        
        # Words that make names look professional
        professional_words = [
            "work", "pro", "business", "office", "design", "dev", "tech", "media", "creative", "digital",
            "studio", "systems", "solutions", "consulting", "info", "contact", "support", "service", "help"
        ]
        
        # Generate random components
        first = random.choice(first_names)
        last = random.choice(last_names)
        year_full = random.randint(1970, 2001)
        year_short = year_full % 100
        random_num = random.randint(1, 999)
        
        # Create patterns that look like legitimate personal email usernames
        patterns = [
            f"{first}.{last}",                         # john.smith
            f"{first}{last}",                          # johnsmith
            f"{first}.{last}{year_short:02d}",         # john.smith89
            f"{first}{last}{random_num}",              # johnsmith123
            f"{first}{year_short:02d}",                # john89
            f"{first[0]}{last}",                       # jsmith
            f"{first}.{last}.{year_short:02d}",        # john.smith.89
            f"{first}_{last}",                         # john_smith
            f"{first}{year_full}",                     # john1989
            f"{last}.{first}",                         # smith.john
            f"{first}.{last}.{random.choice(professional_words)}",  # john.smith.work
            f"{first}{last}{year_short:02d}",          # johnsmith89
            f"{first[0]}{last}{year_short:02d}",       # jsmith89
            f"{first}-{last}"                          # john-smith
        ]
        
        return random.choice(patterns)
    
    def try_tempmail(self):
        """Try to create an email using temp-mail.org (one of the top rated services)"""
        try:
            self.page.get("https://temp-mail.org/")
            time.sleep(3)
            
            # Check if there's a "Change" button which means we already have an email
            change_button = self.page.ele('xpath://button[contains(text(), "Change")]') or self.page.ele('xpath://a[contains(text(), "Change")]')
            if change_button:
                # Already have an email, get it from the input field
                email_field = self.page.ele('xpath://input[@id="mail"]')
                if email_field:
                    email = email_field.attr('value')
                    if email and '@' in email:
                        return email
            
            # If we didn't get an email yet, look for it on the page
            email_field = self.page.ele('xpath://input[@id="mail"]')
            if email_field:
                email = email_field.attr('value')
                if email and '@' in email:
                    return email
            
            return None
        except Exception as e:
            if self.translator:
                print(f"{Fore.YELLOW}⚠️ {self.translator.get('email.tempmail_error')}: {str(e)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠️ temp-mail.org 创建失败: {str(e)}{Style.RESET_ALL}")
            return None
    
    def try_10minutemail(self):
        """Try to create an email using 10minutemail.com"""
        try:
            self.page.get("https://10minutemail.com/")
            time.sleep(3)
            
            # Look for the email address
            email_field = self.page.ele('xpath://input[@id="mailAddress"]')
            if not email_field:
                email_field = self.page.ele('xpath://div[contains(@class, "mail-address-container")]/input')
            
            if email_field:
                email = email_field.attr('value')
                if email and '@' in email:
                    return email
            
            # Try alternative selector
            email_div = self.page.ele('xpath://span[@class="animace"]')
            if email_div:
                email = email_div.text
                if email and '@' in email:
                    return email
            
            return None
        except Exception as e:
            if self.translator:
                print(f"{Fore.YELLOW}⚠️ {self.translator.get('email.10minutemail_error')}: {str(e)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠️ 10minutemail.com 创建失败: {str(e)}{Style.RESET_ALL}")
            return None
    
    def try_emailondeck(self):
        """Try to create an email using EmailOnDeck"""
        try:
            self.page.get("https://www.emailondeck.com/")
            time.sleep(3)
            
            # Look for "Get Email" button
            get_email_button = self.page.ele('xpath://button[contains(text(), "Get Email")]')
            if get_email_button:
                get_email_button.click()
                time.sleep(3)
            
            # Look for the email field
            email_field = self.page.ele('xpath://input[@id="email"]')
            if email_field:
                email = email_field.attr('value')
                if email and '@' in email:
                    return email
            
            # Alternative selector
            email_div = self.page.ele('xpath://span[@id="email"]')
            if email_div:
                email = email_div.text
                if email and '@' in email:
                    return email
            
            return None
        except Exception as e:
            if self.translator:
                print(f"{Fore.YELLOW}⚠️ {self.translator.get('email.emailondeck_error')}: {str(e)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠️ EmailOnDeck 创建失败: {str(e)}{Style.RESET_ALL}")
            return None
    
    def try_yopmail(self):
        """Try to create an email using YOPmail"""
        try:
            # Generate a better looking username first
            username = self.generate_realistic_username()
            
            # Navigate to YOPmail
            self.page.get("https://yopmail.com/")
            time.sleep(2)
            
            # Try to find the email input field
            email_field = self.page.ele('xpath://input[@id="login"]')
            if email_field:
                email_field.click()
                time.sleep(0.5)
                self.page.type(username)
                time.sleep(1)
                
                # Click the check button
                check_button = self.page.ele('xpath://button[@title="Check Inbox" or @class="sbut" or contains(@onclick, "ver")]')
                if check_button:
                    check_button.click()
                    time.sleep(2)
                    return f"{username}@yopmail.com"
            
            return None
        except Exception as e:
            if self.translator:
                print(f"{Fore.YELLOW}⚠️ {self.translator.get('email.yopmail_error')}: {str(e)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠️ YOPmail 创建失败: {str(e)}{Style.RESET_ALL}")
            return None
    
    def try_throwawaymail(self):
        """Try to create an email using ThrowAwayMail"""
        try:
            self.page.get("https://throwawaymail.com/")
            time.sleep(3)
            
            # Look for the email element
            email_element = self.page.ele('xpath://div[contains(@class, "email")]') or self.page.ele('xpath://input[@id="email"]')
            if email_element:
                email = email_element.text or email_element.attr('value')
                if email and '@' in email:
                    return email
            
            return None
        except Exception as e:
            if self.translator:
                print(f"{Fore.YELLOW}⚠️ {self.translator.get('email.throwawaymail_error')}: {str(e)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠️ ThrowAwayMail 创建失败: {str(e)}{Style.RESET_ALL}")
            return None

    def try_mailforspam(self):
        """Create an email using mailforspam.com"""
        try:
            self.page.get("https://mailforspam.com/")
            time.sleep(3)
            
            # Try to find the email address element
            email_elements = self.page.eles('xpath://input[contains(@class, "emailbox-addr")]')
            if email_elements and len(email_elements) > 0:
                email = email_elements[0].attr('value')
                if email and '@' in email:
                    return email
            return None
        except Exception:
            return None

    def try_mailtm(self):
        """Create an email using mail.tm"""
        try:
            self.page.get("https://mail.tm/en/")
            time.sleep(3)
            
            # Generate a better looking username
            username = self.generate_realistic_username()
            
            # Click on the username field and enter the username
            username_field = self.page.ele('xpath://input[@id="address"]')
            if username_field:
                username_field.click()
                time.sleep(0.5)
                self.page.type(username)
                time.sleep(1)
                
                # Click the Create button
                create_button = self.page.ele('xpath://button[contains(text(), "Create account")]')
                if create_button:
                    create_button.click()
                    time.sleep(3)
                    
                    # Try to find the email address element
                    email_element = self.page.ele('xpath://input[@id="address"]')
                    if email_element:
                        email = email_element.attr('value')
                        if email and '@' in email:
                            return email
            return None
        except Exception:
            return None

    def try_tempmail_plus(self):
        """Create an email using tempmail.plus"""
        try:
            self.page.get("https://tempmail.plus/en/")
            time.sleep(3)
            
            # Find and click the random username button
            random_button = self.page.ele('xpath://button[@title="Generate random email address"]')
            if random_button:
                random_button.click()
                time.sleep(2)
                
                # Get the email address
                email_element = self.page.ele('xpath://input[@id="email"]')
                if email_element:
                    email = email_element.attr('value')
                    if email and '@' in email:
                        return email
            return None
        except Exception:
            return None

    def close(self):
        """关闭浏览器"""
        if self.page:
            self.page.quit()

    def refresh_inbox(self):
        """刷新邮箱"""
        try:
            if self.translator:
                print(f"{Fore.CYAN}🔄 {self.translator.get('email.refreshing')}{Style.RESET_ALL}")
            else:
                print(f"{Fore.CYAN}🔄 正在刷新邮箱...{Style.RESET_ALL}")
            
            # 点击刷新按钮
            refresh_button = self.page.ele('xpath://button[@id="refresh"]')
            if refresh_button:
                refresh_button.click()
                time.sleep(2)  # 等待刷新完成
                if self.translator:
                    print(f"{Fore.GREEN}✅ {self.translator.get('email.refresh_success')}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.GREEN}✅ 邮箱刷新成功{Style.RESET_ALL}")
                return True
            
            if self.translator:
                print(f"{Fore.RED}❌ {self.translator.get('email.refresh_button_not_found')}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ 未找到刷新按钮{Style.RESET_ALL}")
            return False
            
        except Exception as e:
            if self.translator:
                print(f"{Fore.RED}❌ {self.translator.get('email.refresh_error')}: {str(e)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ 刷新邮箱出错: {str(e)}{Style.RESET_ALL}")
            return False

    def check_for_cursor_email(self):
        """检查是否有 Cursor 的验证邮件"""
        try:
            # 查找验证邮件 - 使用更精确的选择器
            email_div = self.page.ele('xpath://div[contains(@class, "p-2") and contains(@class, "cursor-pointer") and contains(@class, "bg-white") and contains(@class, "shadow") and .//b[text()="no-reply@cursor.sh"] and .//span[text()="Verify your email address"]]')
            if email_div:
                if self.translator:
                    print(f"{Fore.GREEN}✅ {self.translator.get('email.verification_found')}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.GREEN}✅ 找到验证邮件{Style.RESET_ALL}")
                # 使用 JavaScript 点击元素
                self.page.run_js('arguments[0].click()', email_div)
                time.sleep(2)  # 等待邮件内容加载
                return True
            if self.translator:
                print(f"{Fore.YELLOW}⚠️ {self.translator.get('email.verification_not_found')}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠️ 未找到验证邮件{Style.RESET_ALL}")
            return False
            
        except Exception as e:
            if self.translator:
                print(f"{Fore.RED}❌ {self.translator.get('email.verification_error')}: {str(e)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ 检查验证邮件出错: {str(e)}{Style.RESET_ALL}")
            return False

    def get_verification_code(self):
        """获取验证码"""
        try:
            # 查找验证码元素
            code_element = self.page.ele('xpath://td//div[contains(@style, "font-size:28px") and contains(@style, "letter-spacing:2px")]')
            if code_element:
                code = code_element.text.strip()
                if code.isdigit() and len(code) == 6:
                    if self.translator:
                        print(f"{Fore.GREEN}✅ {self.translator.get('email.verification_code_found')}: {code}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.GREEN}✅ 获取验证码成功: {code}{Style.RESET_ALL}")
                    return code
            if self.translator:
                print(f"{Fore.YELLOW}⚠️ {self.translator.get('email.verification_code_not_found')}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠️ 未找到有效的验证码{Style.RESET_ALL}")
            return None
            
        except Exception as e:
            if self.translator:
                print(f"{Fore.RED}❌ {self.translator.get('email.verification_code_error')}: {str(e)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ 获取验证码出错: {str(e)}{Style.RESET_ALL}")
            return None

def main(translator=None):
    temp_email = NewTempEmail(translator)
    
    try:
        email = temp_email.create_email()
        if email:
            if translator:
                print(f"\n{Fore.CYAN}📧 {translator.get('email.address')}: {email}{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.CYAN}📧 临时邮箱地址: {email}{Style.RESET_ALL}")
            
            # 测试刷新功能
            while True:
                if translator:
                    choice = input(f"\n{translator.get('email.refresh_prompt')}: ").lower()
                else:
                    choice = input("\n按 R 刷新邮箱，按 Q 退出: ").lower()
                if choice == 'r':
                    temp_email.refresh_inbox()
                elif choice == 'q':
                    break
                    
    finally:
        temp_email.close()

if __name__ == "__main__":
    main() 