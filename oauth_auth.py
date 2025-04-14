# oauth_auth.py
import os
from colorama import Fore, Style, init
import time
import random
import webbrowser
import sys
import json
import logging
from DrissionPage import ChromiumPage, ChromiumOptions
from cursor_auth import CursorAuth
from utils import get_random_wait_time, get_default_browser_path
from config import get_config
import platform
from get_user_token import get_token_from_cookie

# Initialize colorama
init()

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Define emoji constants
EMOJI = {
    'START': '🚀',
    'OAUTH': '🔑',
    'SUCCESS': '✅',
    'ERROR': '❌',
    'WAIT': '⏳',
    'INFO': 'ℹ️',
    'WARNING': '⚠️'
}

class OAuthHandler:
    def __init__(self, translator=None, auth_type=None):
        self.translator = translator
        self.config = get_config(translator)
        self.auth_type = auth_type
        os.environ['BROWSER_HEADLESS'] = 'False'
        self.browser = None
        self.selected_profile = None
        
    def _get_available_profiles(self, user_data_dir):
        """Get list of available Chrome profiles with their names"""
        try:
            profiles = []
            profile_names = {}
            
            # Read Local State file to get profile names
            local_state_path = os.path.join(user_data_dir, 'Local State')
            if os.path.exists(local_state_path):
                with open(local_state_path, 'r', encoding='utf-8') as f:
                    local_state = json.load(f)
                    info_cache = local_state.get('profile', {}).get('info_cache', {})
                    for profile_dir, info in info_cache.items():
                        profile_dir = profile_dir.replace('\\', '/')
                        if profile_dir == 'Default':
                            profile_names['Default'] = info.get('name', 'Default')
                        elif profile_dir.startswith('Profile '):
                            profile_names[profile_dir] = info.get('name', profile_dir)

            # Get list of profile directories
            for item in os.listdir(user_data_dir):
                if item == 'Default' or (item.startswith('Profile ') and os.path.isdir(os.path.join(user_data_dir, item))):
                    profiles.append((item, profile_names.get(item, item)))
            return sorted(profiles)
        except Exception as e:
            logger.error(f"Error loading Chrome profiles: {str(e)}")
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('chrome_profile.error_loading', error=str(e)) if self.translator else f'Error loading Chrome profiles: {e}'}{Style.RESET_ALL}")
            return []

    def _select_profile(self):
        """Allow user to select a browser profile to use"""
        try:
            config = get_config(self.translator)
            browser_type = config.get('Browser', 'default_browser', fallback='chrome')
            browser_type_display = browser_type.capitalize()
            
            if self.translator:
                print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('browser_profile.select_profile', browser=browser_type_display)}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{self.translator.get('browser_profile.profile_list', browser=browser_type_display)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.CYAN}{EMOJI['INFO']} Select {browser_type_display} profile to use:{Style.RESET_ALL}")
                print(f"Available {browser_type_display} profiles:")
            
            user_data_dir = self._get_user_data_directory()
            
            try:
                local_state_file = os.path.join(user_data_dir, "Local State")
                if os.path.exists(local_state_file):
                    with open(local_state_file, 'r', encoding='utf-8') as f:
                        state_data = json.load(f)
                    profiles_data = state_data.get('profile', {}).get('info_cache', {})
                    
                    profiles = []
                    for profile_id, profile_info in profiles_data.items():
                        name = profile_info.get('name', profile_id)
                        if profile_id.lower() == 'default':
                            name = f"{name} (Default)"
                        profiles.append((profile_id, name))
                    
                    profiles.sort(key=lambda x: x[1])
                    
                    if self.translator:
                        print(f"{Fore.CYAN}0. {self.translator.get('menu.exit')}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.CYAN}0. Exit{Style.RESET_ALL}")
                    
                    for i, (profile_id, name) in enumerate(profiles, 1):
                        print(f"{Fore.CYAN}{i}. {name}{Style.RESET_ALL}")
                    
                    max_choice = len(profiles)
                    choice_str = input(f"\n{Fore.CYAN}{self.translator.get('menu.input_choice', choices=f'0-{max_choice}') if self.translator else f'Please enter your choice (0-{max_choice})'}{Style.RESET_ALL}")
                    
                    try:
                        choice = int(choice_str)
                        if choice == 0:
                            return False
                        elif 1 <= choice <= max_choice:
                            selected_profile = profiles[choice-1][0]
                            self.selected_profile = selected_profile
                            
                            if self.translator:
                                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('browser_profile.profile_selected', profile=selected_profile)}{Style.RESET_ALL}")
                            else:
                                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Selected profile: {selected_profile}{Style.RESET_ALL}")
                            return True
                        else:
                            if self.translator:
                                print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('browser_profile.invalid_selection')}{Style.RESET_ALL}")
                            else:
                                print(f"{Fore.RED}{EMOJI['ERROR']} Invalid selection. Please try again.{Style.RESET_ALL}")
                            return self._select_profile()
                    except ValueError:
                        if self.translator:
                            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('browser_profile.invalid_selection')}{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.RED}{EMOJI['ERROR']} Invalid selection. Please try again.{Style.RESET_ALL}")
                        return self._select_profile()
                else:
                    print(f"{Fore.YELLOW}{EMOJI['WARNING']} {self.translator.get('browser_profile.no_profiles', browser=browser_type_display) if self.translator else f'No {browser_type_display} profiles found'}{Style.RESET_ALL}")
                    self.selected_profile = "Default"
                    return True
                    
            except Exception as e:
                logger.error(f"Error loading profiles: {str(e)}")
                print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('browser_profile.error_loading', error=str(e), browser=browser_type_display) if self.translator else f'Error loading {browser_type_display} profiles: {str(e)}'}{Style.RESET_ALL}")
                self.selected_profile = "Default"
                return True
            
        except Exception as e:
            logger.error(f"Profile selection error: {str(e)}")
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('oauth.profile_selection_error', error=str(e)) if self.translator else f'Error during profile selection: {str(e)}'}{Style.RESET_ALL}")
            self.selected_profile = "Default"
            return True

    def setup_browser(self):
        """Setup browser for OAuth flow using selected profile"""
        try:
            logger.info("Initializing browser setup")
            print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('oauth.initializing_browser_setup') if self.translator else 'Initializing browser setup...'}{Style.RESET_ALL}")
            
            platform_name = platform.system().lower()
            logger.info(f"Detected platform: {platform_name}")
            print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('oauth.detected_platform', platform=platform_name) if self.translator else f'Detected platform: {platform_name}'}{Style.RESET_ALL}")
            
            config = get_config(self.translator)
            browser_type = config.get('Browser', 'default_browser', fallback='chrome')
            
            user_data_dir = self._get_user_data_directory()
            browser_path = self._get_browser_path()
            
            if not browser_path:
                error_msg = (
                    f"{self.translator.get('oauth.no_compatible_browser_found') if self.translator else 'No compatible browser found. Please install Google Chrome or Chromium.'}" + 
                    "\n" +
                    f"{self.translator.get('oauth.supported_browsers', platform=platform_name)}\n" + 
                    "- Windows: Google Chrome, Chromium\n" +
                    "- macOS: Google Chrome, Chromium\n" +
                    "- Linux: Google Chrome, Chromium, google-chrome-stable"
                )
                logger.error("No compatible browser found")
                raise Exception(error_msg)
            
            logger.info(f"Found browser data directory: {user_data_dir}")
            print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('oauth.found_browser_data_directory', path=user_data_dir) if self.translator else f'Found browser data directory: {user_data_dir}'}{Style.RESET_ALL}")
            
            if self.translator:
                warning_msg = self.translator.get('oauth.warning_browser_close', browser=browser_type)
            else:
                warning_msg = f'Warning: This will close all running {browser_type} processes'
            
            print(f"\n{Fore.YELLOW}{EMOJI['WARNING']} {warning_msg}{Style.RESET_ALL}")
            
            choice = input(f"{Fore.YELLOW} {self.translator.get('menu.continue_prompt', choices='y/N')} {Style.RESET_ALL}").lower()
            if choice != 'y':
                logger.info("Operation cancelled by user")
                print(f"{Fore.YELLOW}{EMOJI['INFO']} {self.translator.get('menu.operation_cancelled_by_user') if self.translator else 'Operation cancelled by user'}{Style.RESET_ALL}")
                return False

            self._kill_browser_processes()
            
            if not self._select_profile():
                logger.info("Operation cancelled by user during profile selection")
                print(f"{Fore.YELLOW}{EMOJI['INFO']} {self.translator.get('menu.operation_cancelled_by_user') if self.translator else 'Operation cancelled by user'}{Style.RESET_ALL}")
                return False
            
            co = self._configure_browser_options(browser_path, user_data_dir, self.selected_profile)
            
            logger.info(f"Starting browser at: {browser_path}")
            print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('oauth.starting_browser', path=browser_path) if self.translator else f'Starting browser at: {browser_path}'}{Style.RESET_ALL}")
            self.browser = ChromiumPage(co)
            
            if not self.browser:
                logger.error("Failed to initialize browser instance")
                raise Exception(f"{self.translator.get('oauth.browser_failed_to_start') if self.translator else 'Failed to initialize browser instance'}")
            
            logger.info("Browser setup completed successfully")
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('oauth.browser_setup_completed') if self.translator else 'Browser setup completed successfully'}{Style.RESET_ALL}")
            return True
            
        except Exception as e:
            logger.error(f"Browser setup failed: {str(e)}", exc_info=True)
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('oauth.browser_setup_failed', error=str(e)) if self.translator else f'Browser setup failed: {str(e)}'}{Style.RESET_ALL}")
            if "DevToolsActivePort file doesn't exist" in str(e):
                print(f"{Fore.YELLOW}{EMOJI['INFO']} {self.translator.get('oauth.try_running_without_sudo_admin') if self.translator else 'Try running without sudo/administrator privileges'}{Style.RESET_ALL}")
            elif "Chrome failed to start" in str(e):
                print(f"{Fore.YELLOW}{EMOJI['INFO']} {self.translator.get('oauth.make_sure_chrome_chromium_is_properly_installed') if self.translator else 'Make sure Chrome/Chromium is properly installed'}{Style.RESET_ALL}")
                if platform_name == 'linux':
                    print(f"{Fore.YELLOW}{EMOJI['INFO']} {self.translator.get('oauth.try_install_chromium') if self.translator else 'Try: sudo apt install chromium-browser'}{Style.RESET_ALL}")
            return False

    def _kill_browser_processes(self):
        """Kill existing browser processes based on platform and browser type"""
        try:
            config = get_config(self.translator)
            browser_type = config.get('Browser', 'default_browser', fallback='chrome')
            browser_type = browser_type.lower()
            
            browser_processes = {
                'chrome': {
                    'win': ['chrome.exe', 'chromium.exe'],
                    'linux': ['chrome', 'chromium', 'chromium-browser', 'google-chrome-stable'],
                    'mac': ['Chrome', 'Chromium']
                },
                'brave': {
                    'win': ['brave.exe'],
                    'linux': ['brave', 'brave-browser'],
                    'mac': ['Brave Browser']
                },
                'edge': {
                    'win': ['msedge.exe'],
                    'linux': ['msedge'],
                    'mac': ['Microsoft Edge']
                },
                'firefox': {
                    'win': ['firefox.exe'],
                    'linux': ['firefox'],
                    'mac': ['Firefox']
                },
                'opera': {
                    'win': ['opera.exe', 'launcher.exe'],
                    'linux': ['opera'],
                    'mac': ['Opera']
                }
            }
            
            if os.name == 'nt':
                platform_type = 'win'
            elif sys.platform == 'darwin':
                platform_type = 'mac'
            else:
                platform_type = 'linux'
            
            processes = browser_processes.get(browser_type, browser_processes['chrome']).get(platform_type, [])
            
            logger.info(f"Killing {browser_type} processes: {processes}")
            print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('oauth.killing_browser_processes', browser=browser_type) if self.translator else f'Killing {browser_type} processes...'}{Style.RESET_ALL}")
            
            if os.name == 'nt':
                for proc in processes:
                    os.system(f'taskkill /f /im {proc} >nul 2>&1')
            else:
                for proc in processes:
                    os.system(f'pkill -f {proc} >/dev/null 2>&1')
            
            time.sleep(1)
        except Exception as e:
            logger.warning(f"Could not kill browser processes: {str(e)}")
            print(f"{Fore.YELLOW}{EMOJI['INFO']} {self.translator.get('oauth.warning_could_not_kill_existing_browser_processes', error=str(e)) if self.translator else f'Warning: Could not kill existing browser processes: {e}'}{Style.RESET_ALL}")

    def _get_user_data_directory(self):
        """Get the default user data directory based on browser type and platform"""
        try:
            config = get_config(self.translator)
            browser_type = config.get('Browser', 'default_browser', fallback='chrome')
            browser_type = browser_type.lower()
            
            if os.name == 'nt':
                user_data_dirs = {
                    'chrome': os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'User Data'),
                    'brave': os.path.join(os.environ.get('LOCALAPPDATA', ''), 'BraveSoftware', 'Brave-Browser', 'User Data'),
                    'edge': os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Edge', 'User Data'),
                    'firefox': os.path.join(os.environ.get('APPDATA', ''), 'Mozilla', 'Firefox', 'Profiles'),
                    'opera': os.path.join(os.environ.get('APPDATA', ''), 'Opera Software', 'Opera Stable'),
                    'operagx': os.path.join(os.environ.get('APPDATA', ''), 'Opera Software', 'Opera GX Stable')
                }
            elif sys.platform == 'darwin':
                user_data_dirs = {
                    'chrome': os.path.expanduser('~/Library/Application Support/Google/Chrome'),
                    'brave': os.path.expanduser('~/Library/Application Support/BraveSoftware/Brave-Browser'),
                    'edge': os.path.expanduser('~/Library/Application Support/Microsoft Edge'),
                    'firefox': os.path.expanduser('~/Library/Application Support/Firefox/Profiles'),
                    'opera': os.path.expanduser('~/Library/Application Support/com.operasoftware.Opera'),
                    'operagx': os.path.expanduser('~/Library/Application Support/com.operasoftware.OperaGX')
                }
            else:
                user_data_dirs = {
                    'chrome': os.path.expanduser('~/.config/google-chrome'),
                    'brave': os.path.expanduser('~/.config/BraveSoftware/Brave-Browser'),
                    'edge': os.path.expanduser('~/.config/microsoft-edge'),
                    'firefox': os.path.expanduser('~/.mozilla/firefox'),
                    'opera': os.path.expanduser('~/.config/opera'),
                    'operagx': os.path.expanduser('~/.config/opera-gx')
                }
            
            user_data_dir = user_data_dirs.get(browser_type)
            
            if user_data_dir and os.path.exists(user_data_dir):
                logger.info(f"Found {browser_type} user data directory: {user_data_dir}")
                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('oauth.found_browser_user_data_dir', browser=browser_type, path=user_data_dir) if self.translator else f'Found {browser_type} user data directory: {user_data_dir}'}{Style.RESET_ALL}")
                return user_data_dir
            else:
                logger.warning(f"{browser_type} user data directory not found at {user_data_dir}, trying Chrome")
                print(f"{Fore.YELLOW}{EMOJI['WARNING']} {self.translator.get('oauth.user_data_dir_not_found', browser=browser_type, path=user_data_dir) if self.translator else f'{browser_type} user data directory not found at {user_data_dir}, will try Chrome instead'}{Style.RESET_ALL}")
                return user_data_dirs['chrome']
            
        except Exception as e:
            logger.error(f"Error getting user data directory: {str(e)}")
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('oauth.error_getting_user_data_directory', error=str(e)) if self.translator else f'Error getting user data directory: {e}'}{Style.RESET_ALL}")
            if os.name == 'nt':
                return os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'User Data')
            elif sys.platform == 'darwin':
                return os.path.expanduser('~/Library/Application Support/Google/Chrome')
            else:
                return os.path.expanduser('~/.config/google-chrome')

    def _get_browser_path(self):
        """Get appropriate browser path based on platform and selected browser type"""
        try:
            config = get_config(self.translator)
            browser_type = config.get('Browser', 'default_browser', fallback='chrome')
            browser_type = browser_type.lower()
            
            browser_path = config.get('Browser', f'{browser_type}_path', fallback=None)
            if browser_path and os.path.exists(browser_path):
                logger.info(f"Using configured {browser_type} path: {browser_path}")
                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('oauth.using_configured_browser_path', browser=browser_type, path=browser_path) if self.translator else f'Using configured {browser_type} path: {browser_path}'}{Style.RESET_ALL}")
                return browser_path
            
            browser_path = get_default_browser_path(browser_type)
            if browser_path and os.path.exists(browser_path):
                return browser_path
            
            logger.info("Searching for alternative browser installations")
            print(f"{Fore.YELLOW}{EMOJI['INFO']} {self.translator.get('oauth.searching_for_alternative_browser_installations') if self.translator else 'Searching for alternative browser installations...'}{Style.RESET_ALL}")
            
            if os.name == 'nt':
                possible_paths = []
                if browser_type == 'brave':
                    possible_paths = [
                        os.path.join(os.environ.get('PROGRAMFILES', ''), 'BraveSoftware', 'Brave-Browser', 'Application', 'brave.exe'),
                        os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'BraveSoftware', 'Brave-Browser', 'Application', 'brave.exe'),
                        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'BraveSoftware', 'Brave-Browser', 'Application', 'brave.exe')
                    ]
                elif browser_type == 'edge':
                    possible_paths = [
                        os.path.join(os.environ.get('PROGRAMFILES', ''), 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
                        os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'Microsoft', 'Edge', 'Application', 'msedge.exe')
                    ]
                elif browser_type == 'firefox':
                    possible_paths = [
                        os.path.join(os.environ.get('PROGRAMFILES', ''), 'Mozilla Firefox', 'firefox.exe'),
                        os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'Mozilla Firefox', 'firefox.exe')
                    ]
                elif browser_type == 'opera':
                    possible_paths = [
                        os.path.join(os.environ.get('PROGRAMFILES', ''), 'Opera', 'opera.exe'),
                        os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'Opera', 'opera.exe'),
                        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Opera', 'launcher.exe'),
                        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Opera', 'opera.exe'),
                        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Opera GX', 'launcher.exe'),
                        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Opera GX', 'opera.exe')
                    ]
                else:
                    possible_paths = [
                        os.path.join(os.environ.get('PROGRAMFILES', ''), 'Google', 'Chrome', 'Application', 'chrome.exe'),
                        os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'Google', 'Chrome', 'Application', 'chrome.exe'),
                        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'Application', 'chrome.exe')
                    ]
                
            elif sys.platform == 'darwin':
                possible_paths = []
                if browser_type == 'brave':
                    possible_paths = ['/Applications/Brave Browser.app/Contents/MacOS/Brave Browser']
                elif browser_type == 'edge':
                    possible_paths = ['/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge']
                elif browser_type == 'firefox':
                    possible_paths = ['/Applications/Firefox.app/Contents/MacOS/firefox']
                else:
                    possible_paths = ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome']
                
            else:
                possible_paths = []
                if browser_type == 'brave':
                    possible_paths = ['/usr/bin/brave-browser', '/usr/bin/brave']
                elif browser_type == 'edge':
                    possible_paths = ['/usr/bin/microsoft-edge']
                elif browser_type == 'firefox':
                    possible_paths = ['/usr/bin/firefox']
                else:
                    possible_paths = [
                        '/usr/bin/google-chrome-stable',
                        '/usr/bin/google-chrome',
                        '/usr/bin/chromium',
                        '/usr/bin/chromium-browser'
                    ]
                
            for path in possible_paths:
                if os.path.exists(path):
                    logger.info(f"Found browser at: {path}")
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('oauth.found_browser_at', path=path) if self.translator else f'Found browser at: {path}'}{Style.RESET_ALL}")
                    return path
            
            if browser_type != 'chrome':
                logger.warning(f"Could not find {browser_type}, trying Chrome")
                print(f"{Fore.YELLOW}{EMOJI['WARNING']} {self.translator.get('oauth.browser_not_found_trying_chrome', browser=browser_type) if self.translator else f'Could not find {browser_type}, trying Chrome instead'}{Style.RESET_ALL}")
                return self._get_chrome_path()
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding browser path: {str(e)}", exc_info=True)
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('oauth.error_finding_browser_path', error=str(e)) if self.translator else f'Error finding browser path: {e}'}{Style.RESET_ALL}")
            return None

    def _configure_browser_options(self, browser_path, user_data_dir, active_profile):
        """Configure browser options based on platform"""
        try:
            co = ChromiumOptions()
            co.set_paths(browser_path=browser_path, user_data_path=user_data_dir)
            co.set_argument(f'--profile-directory={active_profile}')
            
            co.set_argument('--no-first-run')
            co.set_argument('--no-default-browser-check')
            co.set_argument('--disable-gpu')
            co.set_argument('--remote-debugging-port=9222')
            
            if sys.platform.startswith('linux'):
                co.set_argument('--no-sandbox')
                co.set_argument('--disable-dev-shm-usage')
                co.set_argument('--disable-setuid-sandbox')
            elif sys.platform == 'darwin':
                co.set_argument('--disable-gpu-compositing')
            elif os.name == 'nt':
                co.set_argument('--disable-features=TranslateUI')
                co.set_argument('--disable-features=RendererCodeIntegrity')
            
            logger.info("Browser options configured successfully")
            return co
            
        except Exception as e:
            logger.error(f"Error configuring browser options: {str(e)}", exc_info=True)
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('oauth.error_configuring_browser_options', error=str(e)) if self.translator else f'Error configuring browser options: {e}'}{Style.RESET_ALL}")
            raise

    def handle_google_auth(self):
        """Handle Google OAuth authentication"""
        try:
            logger.info("Starting Google OAuth authentication")
            print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('oauth.google_start') if self.translator else 'Starting Google OAuth authentication...'}{Style.RESET_ALL}")
            
            if not self.setup_browser():
                logger.error("Browser failed to initialize")
                print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('oauth.browser_failed') if self.translator else 'Browser failed to initialize'}{Style.RESET_ALL}")
                return False, None
            
            try:
                logger.info("Navigating to authentication page")
                print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('oauth.navigating_to_authentication_page') if self.translator else 'Navigating to authentication page...'}{Style.RESET_ALL}")
                self.browser.get("https://authenticator.cursor.sh/sign-up")
                time.sleep(get_random_wait_time(self.config, 'page_load_wait'))
                logger.info(f"Current URL after navigation: {self.browser.url}")
                
                selectors = [
                    "//a[contains(@href,'GoogleOAuth')]",
                    "//a[contains(@class,'auth-method-button') and contains(@href,'GoogleOAuth')]",
                    "(//a[contains(@class,'auth-method-button')])[1]"
                ]
                
                auth_btn = None
                for selector in selectors:
                    logger.debug(f"Trying selector: {selector}")
                    try:
                        auth_btn = self.browser.ele(f"xpath:{selector}", timeout=5)
                        if auth_btn and auth_btn.is_displayed():
                            logger.info(f"Found Google auth button with selector: {selector}")
                            break
                    except Exception as e:
                        logger.warning(f"Selector {selector} failed: {str(e)}")
                        continue
                
                if not auth_btn:
                    logger.error("Could not find Google authentication button")
                    raise Exception("Could not find Google authentication button")
                
                logger.debug(f"Button state - displayed: {auth_btn.is_displayed()}, enabled: {auth_btn.is_enabled()}")
                print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('oauth.starting_google_authentication') if self.translator else 'Starting Google authentication...'}{Style.RESET_ALL}")
                try:
                    auth_btn.click()
                except Exception as e:
                    logger.warning(f"Standard click failed: {str(e)}, attempting JavaScript click")
                    self.browser.run_js("arguments[0].click();", auth_btn)
                time.sleep(get_random_wait_time(self.config, 'page_load_wait'))
                
                if "accounts.google.com" in self.browser.url:
                    logger.info("On Google account selection page")
                    print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('oauth.please_select_your_google_account_to_continue') if self.translator else 'Please select your Google account to continue...'}{Style.RESET_ALL}")
                    
                    config = get_config(self.translator)
                    show_alert = config.getboolean('OAuth', 'show_selection_alert', fallback=False)
                    
                    if show_alert:
                        alert_message = self.translator.get('oauth.please_select_your_google_account_to_continue') if self.translator else 'Please select your Google account to continue with Cursor authentication'
                        try:
                            self.browser.run_js(f"""
                            alert('{alert_message}');
                            """)
                        except:
                            logger.warning("Failed to display alert")
                            pass
                
                auth_info = self._wait_for_auth()
                if not auth_info:
                    logger.error("Authentication timeout")
                    print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('oauth.timeout') if self.translator else 'Timeout'}{Style.RESET_ALL}")
                    return False, None
                
                logger.info("Google authentication successful")
                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('oauth.success') if self.translator else 'Success'}{Style.RESET_ALL}")
                return True, auth_info
                
            except Exception as e:
                logger.error(f"Authentication error: {str(e)}", exc_info=True)
                print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('oauth.authentication_error', error=str(e)) if self.translator else f'Authentication error: {str(e)}'}{Style.RESET_ALL}")
                return False, None
            finally:
                try:
                    if self.browser:
                        self.browser.quit()
                        logger.info("Browser closed")
                except:
                    logger.warning("Failed to close browser")
                    pass
            
        except Exception as e:
            logger.error(f"Google OAuth failed: {str(e)}", exc_info=True)
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('oauth.failed', error=str(e))}{Style.RESET_ALL}")
            return False, None

    def _wait_for_auth(self):
        """Wait for authentication to complete and extract auth info"""
        try:
            max_wait = 300
            start_time = time.time()
            check_interval = 2
            
            logger.info("Waiting for authentication (timeout: 5 minutes)")
            print(f"{Fore.CYAN}{EMOJI['WAIT']} {self.translator.get('oauth.waiting_for_authentication', timeout='5 minutes') if self.translator else 'Waiting for authentication (timeout: 5 minutes)'}{Style.RESET_ALL}")
            
            while time.time() - start_time < max_wait:
                try:
                    cookies = self.browser.cookies()
                    
                    for cookie in cookies:
                        if cookie.get("name") == "WorkosCursorSessionToken":
                            value = cookie.get("value", "")
                            token = get_token_from_cookie(value, self.translator)
                            if token:
                                logger.info("Authentication successful, getting account info")
                                print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('oauth.authentication_successful_getting_account_info') if self.translator else 'Authentication successful, getting account info...'}{Style.RESET_ALL}")
                                self.browser.get("https://www.cursor.com/settings")
                                time.sleep(3)
                                
                                email = None
                                try:
                                    email_element = self.browser.ele("css:div[class='flex w-full flex-col gap-2'] div:nth-child(2) p:nth-child(2)")
                                    if email_element:
                                        email = email_element.text
                                        logger.info(f"Found email: {email}")
                                        print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('oauth.found_email', email=email) if self.translator else f'Found email: {email}'}{Style.RESET_ALL}")
                                except:
                                    logger.warning("Could not find email, using fallback")
                                    email = "user@cursor.sh"
                                
                                try:
                                    usage_element = self.browser.ele("css:div[class='flex flex-col gap-4 lg:flex-row'] div:nth-child(1) div:nth-child(1) span:nth-child(2)")
                                    if usage_element:
                                        usage_text = usage_element.text
                                        logger.info(f"Usage count: {usage_text}")
                                        print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('oauth.usage_count', usage=usage_text) if self.translator else f'Usage count: {usage_text}'}{Style.RESET_ALL}")
                                        
                                        def check_usage_limits(usage_str):
                                            try:
                                                parts = usage_str.split('/')
                                                if len(parts) != 2:
                                                    return False
                                                current = int(parts[0].strip())
                                                limit = int(parts[1].strip())
                                                return (limit == 50 and current >= 50) or (limit == 150 and current >= 150)
                                            except:
                                                return False

                                        if check_usage_limits(usage_text):
                                            logger.info("Account has reached maximum usage, deleting")
                                            print(f"{Fore.YELLOW}{EMOJI['INFO']} {self.translator.get('oauth.account_has_reached_maximum_usage', deleting='deleting') if self.translator else 'Account has reached maximum usage, deleting...'}{Style.RESET_ALL}")
                                            if self._delete_current_account():
                                                logger.info("Starting new authentication process")
                                                print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('oauth.starting_new_authentication_process') if self.translator else 'Starting new authentication process...'}{Style.RESET_ALL}")
                                                if self.auth_type == "google":
                                                    return self.handle_google_auth()
                                                else:
                                                    return self.handle_github_auth()
                                            else:
                                                logger.error("Failed to delete expired account")
                                                print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('oauth.failed_to_delete_expired_account') if self.translator else 'Failed to delete expired account'}{Style.RESET_ALL}")
                                        else:
                                            logger.info(f"Account is still valid (Usage: {usage_text})")
                                            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('oauth.account_is_still_valid', usage=usage_text) if self.translator else f'Account is still valid (Usage: {usage_text})'}{Style.RESET_ALL}")
                                except Exception as e:
                                    logger.warning(f"Could not check usage count: {str(e)}")
                                    print(f"{Fore.YELLOW}{EMOJI['INFO']} {self.translator.get('oauth.could_not_check_usage_count', error=str(e)) if self.translator else f'Could not check usage count: {str(e)}'}{Style.RESET_ALL}")
                                
                                return {"email": email, "token": token}
                    
                    if "cursor.com/settings" in self.browser.url:
                        logger.info("Detected successful login via URL")
                        print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('oauth.detected_successful_login') if self.translator else 'Detected successful login'}{Style.RESET_ALL}")
                    
                except Exception as e:
                    logger.warning(f"Error during auth wait: {str(e)}")
                    print(f"{Fore.YELLOW}{EMOJI['INFO']} {self.translator.get('oauth.waiting_for_authentication', error=str(e)) if self.translator else f'Waiting for authentication... ({str(e)})'}{Style.RESET_ALL}")
                
                time.sleep(check_interval)
            
            logger.error("Authentication timeout")
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('oauth.authentication_timeout') if self.translator else 'Authentication timeout'}{Style.RESET_ALL}")
            return None
            
        except Exception as e:
            logger.error(f"Error waiting for authentication: {str(e)}", exc_info=True)
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('oauth.error_waiting_for_authentication', error=str(e)) if self.translator else f'Error while waiting for authentication: {str(e)}'}{Style.RESET_ALL}")
            return None
        
    def handle_github_auth(self):
        """Handle GitHub OAuth authentication"""
        try:
            logger.info("Starting GitHub OAuth authentication")
            print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('oauth.github_start')}{Style.RESET_ALL}")
            
            if not self.setup_browser():
                logger.error("Browser failed to initialize")
                print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('oauth.browser_failed') if self.translator else 'Browser failed to initialize'}{Style.RESET_ALL}")
                return False, None
            
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    logger.info(f"Attempt {attempt + 1}/{max_retries}: Navigating to authentication page")
                    print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('oauth.navigating_to_authentication_page') if self.translator else 'Navigating to authentication page...'}{Style.RESET_ALL}")
                    self.browser.get("https://authenticator.cursor.sh/sign-up")
                    time.sleep(get_random_wait_time(self.config, 'page_load_wait'))
                    logger.info(f"Current URL after navigation: {self.browser.url}")
                    
                    selectors = [
                        "//a[contains(@href,'GitHubOAuth')]",
                        "//a[contains(@class,'auth-method-button') and contains(@href,'GitHubOAuth')]",
                        "(//a[contains(@class,'auth-method-button')])[2]",
                        "//a[contains(text(),'GitHub')]",
                        "//a[@href='/auth/github']"
                    ]
                    
                    auth_btn = None
                    for selector in selectors:
                        logger.debug(f"Trying selector: {selector}")
                        try:
                            auth_btn = self.browser.ele(f"xpath:{selector}", timeout=5)
                            if auth_btn and auth_btn.is_displayed():
                                logger.info(f"Found GitHub auth button with selector: {selector}")
                                break
                        except Exception as e:
                            logger.warning(f"Selector {selector} failed: {str(e)}")
                            continue
                    
                    if not auth_btn:
                        logger.error("Could not find GitHub authentication button")
                        raise Exception("Could not find GitHub authentication button")
                    
                    logger.debug(f"Button state - displayed: {auth_btn.is_displayed()}, enabled: {auth_btn.is_enabled()}")
                    print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('oauth.starting_github_authentication') if self.translator else 'Starting GitHub authentication...'}{Style.RESET_ALL}")
                    try:
                        auth_btn.click()
                    except Exception as e:
                        logger.warning(f"Standard click failed: {str(e)}, attempting JavaScript click")
                        self.browser.run_js("arguments[0].click();", auth_btn)
                    time.sleep(get_random_wait_time(self.config, 'page_load_wait'))
                    logger.info(f"Current URL after clicking GitHub button: {self.browser.url}")
                    
                    auth_info = self._wait_for_auth()
                    if not auth_info:
                        logger.error("Authentication timeout")
                        print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('oauth.timeout') if self.translator else 'Timeout'}{Style.RESET_ALL}")
                        return False, None
                    
                    logger.info("GitHub authentication successful")
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('oauth.success')}{Style.RESET_ALL}")
                    return True, auth_info
                    
                except Exception as e:
                    logger.error(f"Attempt {attempt + 1} failed: {str(e)}", exc_info=True)
                    print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('oauth.authentication_error', error=str(e)) if self.translator else f'Authentication error: {str(e)}'}{Style.RESET_ALL}")
                    if attempt < max_retries - 1:
                        logger.info("Retrying navigation")
                        time.sleep(2)
                        continue
                    return False, None
                finally:
                    try:
                        if self.browser and attempt == max_retries - 1:
                            self.browser.quit()
                            logger.info("Browser closed")
                    except:
                        logger.warning("Failed to close browser")
                        pass
            
        except Exception as e:
            logger.error(f"GitHub OAuth failed: {str(e)}", exc_info=True)
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('oauth.failed', error=str(e))}{Style.RESET_ALL}")
            return False, None
        
    def _handle_oauth(self, auth_type):
        """Handle OAuth authentication for both Google and GitHub"""
        try:
            if not self.setup_browser():
                return False, None
                
            self.browser.get("https://authenticator.cursor.sh/sign-up")
            time.sleep(get_random_wait_time(self.config, 'page_load_wait'))
            logger.info(f"Current URL in _handle_oauth: {self.browser.url}")
            
            if auth_type == "google":
                selectors = [
                    "//a[@class='rt-reset rt-BaseButton rt-r-size-3 rt-variant-surface rt-high-contrast rt-Button auth-method-button_AuthMethodButton__irESX'][contains(@href,'GoogleOAuth')]",
                    "(//a[@class='rt-reset rt-BaseButton rt-r-size-3 rt-variant-surface rt-high-contrast rt-Button auth-method-button_AuthMethodButton__irESX'])[1]"
                ]
            else:
                selectors = [
                    "(//a[@class='rt-reset rt-BaseButton rt-r-size-3 rt-variant-surface rt-high-contrast rt-Button auth-method-button_AuthMethodButton__irESX'])[2]"
                ]
            
            auth_btn = None
            max_button_wait = 30
            button_start_time = time.time()
            
            while time.time() - button_start_time < max_button_wait:
                for selector in selectors:
                    logger.debug(f"Trying selector in _handle_oauth: {selector}")
                    try:
                        auth_btn = self.browser.ele(f"xpath:{selector}", timeout=1)
                        if auth_btn and auth_btn.is_displayed():
                            logger.info(f"Found auth button in _handle_oauth: {selector}")
                            break
                    except:
                        continue
                if auth_btn:
                    break
                time.sleep(1)
            
            if auth_btn:
                logger.debug(f"Button state in _handle_oauth - displayed: {auth_btn.is_displayed()}, enabled: {auth_btn.is_enabled()}")
                auth_btn.click()
                time.sleep(get_random_wait_time(self.config, 'page_load_wait'))
                
                if auth_type == "google" and "accounts.google.com" in self.browser.url:
                    alert_message = self.translator.get('oauth.please_select_your_google_account_to_continue') if self.translator else 'Please select your Google account to continue with Cursor authentication'
                    try:
                        self.browser.run_js(f"""
                        alert('{alert_message}');
                        """)
                    except Exception as e:
                        logger.warning(f"Alert display failed: {str(e)}")
                        print(f"{Fore.YELLOW}{EMOJI['INFO']} {self.translator.get('oauth.alert_display_failed', error=str(e)) if self.translator else f'Alert display failed: {str(e)}'}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('oauth.please_select_your_google_account_manually_to_continue_with_cursor_authentication') if self.translator else 'Please select your Google account manually to continue with Cursor authentication...'}{Style.RESET_ALL}")
                
                print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('oauth.waiting_for_authentication_to_complete') if self.translator else 'Waiting for authentication to complete...'}{Style.RESET_ALL}")
                
                max_wait = 300
                start_time = time.time()
                last_url = self.browser.url
                
                print(f"{Fore.CYAN}{EMOJI['WAIT']} {self.translator.get('oauth.checking_authentication_status') if self.translator else 'Checking authentication status...'}{Style.RESET_ALL}")
                
                while time.time() - start_time < max_wait:
                    try:
                        cookies = self.browser.cookies()
                        
                        for cookie in cookies:
                            if cookie.get("name") == "WorkosCursorSessionToken":
                                value = cookie.get("value", "")
                                token = get_token_from_cookie(value, self.translator)
                                if token:
                                    logger.info("Authentication successful in _handle_oauth")
                                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('oauth.authentication_successful') if self.translator else 'Authentication successful!'}{Style.RESET_ALL}")
                                    print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('oauth.navigating_to_settings_page') if self.translator else 'Navigating to settings page...'}{Style.RESET_ALL}")
                                    self.browser.get("https://www.cursor.com/settings")
                                    time.sleep(3)
                                    
                                    try:
                                        email_element = self.browser.ele("css:div[class='flex w-full flex-col gap-2'] div:nth-child(2) p:nth-child(2)")
                                        if email_element:
                                            actual_email = email_element.text
                                            logger.info(f"Found email: {actual_email}")
                                            print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('oauth.found_email', email=actual_email) if self.translator else f'Found email: {actual_email}'}{Style.RESET_ALL}")
                                    except Exception as e:
                                        logger.warning(f"Could not find email: {str(e)}")
                                        print(f"{Fore.YELLOW}{EMOJI['INFO']} {self.translator.get('oauth.could_not_find_email', error=str(e)) if self.translator else f'Could not find email: {str(e)}'}{Style.RESET_ALL}")
                                        actual_email = "user@cursor.sh"
                                    
                                    try:
                                        usage_element = self.browser.ele("css:div[class='flex flex-col gap-4 lg:flex-row'] div:nth-child(1) div:nth-child(1) span:nth-child(2)")
                                        if usage_element:
                                            usage_text = usage_element.text
                                            logger.info(f"Usage count: {usage_text}")
                                            print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('oauth.usage_count', usage=usage_text) if self.translator else f'Usage count: {usage_text}'}{Style.RESET_ALL}")
                                            
                                            def check_usage_limits(usage_str):
                                                try:
                                                    parts = usage_str.split('/')
                                                    if len(parts) != 2:
                                                        return False
                                                    current = int(parts[0].strip())
                                                    limit = int(parts[1].strip())
                                                    return (limit == 50 and current >= 50) or (limit == 150 and current >= 150)
                                                except:
                                                    return False

                                            if check_usage_limits(usage_text):
                                                logger.info("Account has reached maximum usage, deleting")
                                                print(f"{Fore.YELLOW}{EMOJI['INFO']} {self.translator.get('oauth.account_has_reached_maximum_usage', deleting='deleting') if self.translator else 'Account has reached maximum usage, deleting...'}{Style.RESET_ALL}")
                                                if self._delete_current_account():
                                                    logger.info("Starting new authentication process")
                                                    print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('oauth.starting_new_authentication_process') if self.translator else 'Starting new authentication process...'}{Style.RESET_ALL}")
                                                    if self.auth_type == "google":
                                                        return self.handle_google_auth()
                                                    else:
                                                        return self.handle_github_auth()
                                                else:
                                                    logger.error("Failed to delete expired account")
                                                    print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('oauth.failed_to_delete_expired_account') if self.translator else 'Failed to delete expired account'}{Style.RESET_ALL}")
                                            else:
                                                logger.info(f"Account is still valid (Usage: {usage_text})")
                                                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('oauth.account_is_still_valid', usage=usage_text) if self.translator else f'Account is still valid (Usage: {usage_text})'}{Style.RESET_ALL}")
                                    except Exception as e:
                                        logger.warning(f"Could not check usage count: {str(e)}")
                                        print(f"{Fore.YELLOW}{EMOJI['INFO']} {self.translator.get('oauth.could_not_check_usage_count', error=str(e)) if self.translator else f'Could not check usage count: {str(e)}'}{Style.RESET_ALL}")
                                    
                                    return True, {"email": actual_email, "token": token}
                        
                        current_url = self.browser.url
                        if "cursor.com/settings" in current_url:
                            logger.info("Already on settings page")
                            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('oauth.already_on_settings_page') if self.translator else 'Already on settings page!'}{Style.RESET_ALL}")
                            time.sleep(1)
                            cookies = self.browser.cookies()
                            for cookie in cookies:
                                if cookie.get("name") == "WorkosCursorSessionToken":
                                    value = cookie.get("value", "")
                                    token = get_token_from_cookie(value, self.translator)
                                    if token:
                                        try:
                                            email_element = self.browser.ele("css:div[class='flex w-full flex-col gap-2'] div:nth-child(2) p:nth-child(2)")
                                            if email_element:
                                                actual_email = email_element.text
                                                logger.info(f"Found email: {actual_email}")
                                                print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('oauth.found_email', email=actual_email) if self.translator else f'Found email: {actual_email}'}{Style.RESET_ALL}")
                                        except Exception as e:
                                            logger.warning(f"Could not find email: {str(e)}")
                                            print(f"{Fore.YELLOW}{EMOJI['INFO']} {self.translator.get('oauth.could_not_find_email', error=str(e)) if self.translator else f'Could not find email: {str(e)}'}{Style.RESET_ALL}")
                                            actual_email = "user@cursor.sh"
                                        
                                        try:
                                            usage_element = self.browser.ele("css:div[class='flex flex-col gap-4 lg:flex-row'] div:nth-child(1) div:nth-child(1) span:nth-child(2)")
                                            if usage_element:
                                                usage_text = usage_element.text
                                                logger.info(f"Usage count: {usage_text}")
                                                print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('oauth.usage_count', usage=usage_text) if self.translator else f'Usage count: {usage_text}'}{Style.RESET_ALL}")
                                                
                                                def check_usage_limits(usage_str):
                                                    try:
                                                        parts = usage_str.split('/')
                                                        if len(parts) != 2:
                                                            return False
                                                        current = int(parts[0].strip())
                                                        limit = int(parts[1].strip())
                                                        return (limit == 50 and current >= 50) or (limit == 150 and current >= 150)
                                                    except:
                                                        return False

                                            if check_usage_limits(usage_text):
                                                logger.info("Account has reached maximum usage, deleting")
                                                print(f"{Fore.YELLOW}{EMOJI['INFO']} {self.translator.get('oauth.account_has_reached_maximum_usage', deleting='deleting') if self.translator else 'Account has reached maximum usage, deleting...'}{Style.RESET_ALL}")
                                                if self._delete_current_account():
                                                    logger.info("Starting new authentication process")
                                                    print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('oauth.starting_new_authentication_process') if self.translator else 'Starting new authentication process...'}{Style.RESET_ALL}")
                                                    if self.auth_type == "google":
                                                        return self.handle_google_auth()
                                                    else:
                                                        return self.handle_github_auth()
                                                else:
                                                    logger.error("Failed to delete expired account")
                                                    print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('oauth.failed_to_delete_expired_account') if self.translator else 'Failed to delete expired account'}{Style.RESET_ALL}")
                                            else:
                                                logger.info(f"Account is still valid (Usage: {usage_text})")
                                                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('oauth.account_is_still_valid', usage=usage_text) if self.translator else f'Account is still valid (Usage: {usage_text})'}{Style.RESET_ALL}")
                                        except Exception as e:
                                            logger.warning(f"Could not check usage count: {str(e)}")
                                            print(f"{Fore.YELLOW}{EMOJI['INFO']} {self.translator.get('oauth.could_not_check_usage_count', error=str(e)) if self.translator else f'Could not check usage count: {str(e)}'}{Style.RESET_ALL}")
                                        
                                        return True, {"email": actual_email, "token": token}
                        elif current_url != last_url:
                            logger.info(f"Page changed to {current_url}")
                            print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('oauth.page_changed_checking_auth') if self.translator else 'Page changed, checking auth...'}{Style.RESET_ALL}")
                            last_url = current_url
                            time.sleep(get_random_wait_time(self.config, 'page_load_wait'))
                    except Exception as e:
                        logger.warning(f"Status check error: {str(e)}")
                        print(f"{Fore.YELLOW}{EMOJI['INFO']} {self.translator.get('oauth.status_check_error', error=str(e)) if self.translator else f'Status check error: {str(e)}'}{Style.RESET_ALL}")
                        time.sleep(1)
                        continue
                    time.sleep(1)
                    
                logger.error("Authentication timeout")
                print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('oauth.authentication_timeout') if self.translator else 'Authentication timeout'}{Style.RESET_ALL}")
                return False, None
                
            logger.error("Authentication button not found")
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('oauth.authentication_button_not_found') if self.translator else 'Authentication button not found'}{Style.RESET_ALL}")
            return False, None
            
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}", exc_info=True)
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('oauth.authentication_failed', error=str(e)) if self.translator else f'Authentication failed: {str(e)}'}{Style.RESET_ALL}")
            return False, None
        finally:
            if self.browser:
                self.browser.quit()
                logger.info("Browser closed in _handle_oauth")

    def _extract_auth_info(self):
        """Extract authentication information after successful OAuth"""
        try:
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    cookies = self.browser.cookies()
                    if cookies:
                        break
                    time.sleep(1)
                except:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(1)
            
            logger.info(f"Found {len(cookies)} cookies")
            print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('oauth.found_cookies', count=len(cookies)) if self.translator else f'Found {len(cookies)} cookies'}{Style.RESET_ALL}")
            
            email = None
            token = None
            
            for cookie in cookies:
                name = cookie.get("name", "")
                if name == "WorkosCursorSessionToken":
                    try:
                        value = cookie.get("value", "")
                        token = get_token_from_cookie(value, self.translator)
                    except Exception as e:
                        logger.error(f"Failed to extract token: {str(e)}")
                        error_message = f'Failed to extract auth info: {str(e)}' if not self.translator else self.translator.get('oauth.failed_to_extract_auth_info', error=str(e))
                        print(f"{Fore.RED}{EMOJI['ERROR']} {error_message}{Style.RESET_ALL}")
                elif name == "cursor_email":
                    email = cookie.get("value")
                    
            if email and token:
                logger.info(f"Authentication successful - Email: {email}")
                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('oauth.authentication_successful', email=email) if self.translator else f'Authentication successful - Email: {email}'}{Style.RESET_ALL}")
                return True, {"email": email, "token": token}
            else:
                missing = []
                if not email:
                    missing.append("email")
                if not token:
                    missing.append("token")
                logger.error(f"Missing authentication data: {', '.join(missing)}")
                error_message = f"Missing authentication data: {', '.join(missing)}" if not self.translator else self.translator.get('oauth.missing_authentication_data', data=', '.join(missing))
                print(f"{Fore.RED}{EMOJI['ERROR']} {error_message}{Style.RESET_ALL}")
                return False, None
            
        except Exception as e:
            logger.error(f"Failed to extract auth info: {str(e)}", exc_info=True)
            error_message = f'Failed to extract auth info: {str(e)}' if not self.translator else self.translator.get('oauth.failed_to_extract_auth_info', error=str(e))
            print(f"{Fore.RED}{EMOJI['ERROR']} {error_message}{Style.RESET_ALL}")
            return False, None

    def _delete_current_account(self):
        """Delete the current account using the API"""
        try:
            delete_js = """
            function deleteAccount() {
                return new Promise((resolve, reject) => {
                    fetch('https://www.cursor.com/api/dashboard/delete-account', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        credentials: 'include'
                    })
                    .then(response => {
                        if (response.status === 200) {
                            resolve('Account deleted successfully');
                        } else {
                            reject('Failed to delete account: ' + response.status);
                        }
                    })
                    .catch(error => {
                        reject('Error: ' + error);
                    });
                });
            }
            return deleteAccount();
            """
            
            logger.info("Attempting to delete account via API")
            result = self.browser.run_js(delete_js)
            logger.info(f"Delete account result: {result}")
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {self.translator.get('oauth.delete_account_success', result=result) if self.translator else f'Delete account result: {result}'}{Style.RESET_ALL}")
            
            logger.info("Redirecting to authenticator.cursor.sh")
            print(f"{Fore.CYAN}{EMOJI['INFO']} {self.translator.get('oauth.redirecting_to_authenticator_cursor_sh') if self.translator else 'Redirecting to authenticator.cursor.sh...'}{Style.RESET_ALL}")
            self.browser.get("https://authenticator.cursor.sh/sign-up")
            time.sleep(get_random_wait_time(self.config, 'page_load_wait'))
            logger.info(f"Navigated to sign-up page: {self.browser.url}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete account: {str(e)}", exc_info=True)
            error_message = self.translator.get('oauth.failed_to_delete_account', error=str(e)) if self.translator else f'Failed to delete account: {str(e)}'
            print(f"{Fore.RED}{EMOJI['ERROR']} {error_message}{Style.RESET_ALL}")
            return False