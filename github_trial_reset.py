import os
import time
from colorama import init, Fore
from DrissionPage import ChromiumPage
from cursor_auth import CursorAuth
from utils import MachineIDResetter
import keyring

# Initialize colorama
init()

# Emoji constants
CHECK_MARK = "✓"
CROSS_MARK = "❌"

def get_saved_credentials():
    """Retrieve saved GitHub credentials from keyring."""
    try:
        email = keyring.get_password("cursor-github", "email")
        password = keyring.get_password("cursor-github", "password")
        return email, password
    except Exception:
        return None, None

def save_credentials(email, password):
    """Save GitHub credentials to keyring."""
    try:
        keyring.set_password("cursor-github", "email", email)
        keyring.set_password("cursor-github", "password", password)
        return True
    except Exception:
        return False

def extract_auth_data(page, github_email=None):
    """Extract authentication data from the page."""
    print(f"\n{Fore.CYAN}Checking cookies...{Fore.RESET}")
    cookies = page.get_cookies()
    print(f"Found {len(cookies)} cookies")
    
    for cookie in cookies:
        print(f"Cookie: {cookie['name']} = {cookie['value'][:10]}...")
    
    auth_token = None
    cursor_email = None
    
    # Try to get token from cookies with different separators
    for cookie in cookies:
        if cookie['name'] == 'WorkosCursorSessionToken':
            value = cookie['value']
            if '::' in value:
                auth_token = value.split('::')[1]
            elif '%3A%3A' in value:
                auth_token = value.split('%3A%3A')[1]
            if auth_token:
                print(f"{CHECK_MARK} Found auth token: {auth_token[:10]}...")
                break
    
    # Try to get token from localStorage if not found in cookies
    if not auth_token:
        try:
            local_storage = page.get_local_storage()
            if 'WorkosCursorSessionToken' in local_storage:
                value = local_storage['WorkosCursorSessionToken']
                if '::' in value:
                    auth_token = value.split('::')[1]
                elif '%3A%3A' in value:
                    auth_token = value.split('%3A%3A')[1]
                if auth_token:
                    print(f"{CHECK_MARK} Found auth token in localStorage: {auth_token[:10]}...")
        except Exception as e:
            print(f"{CROSS_MARK} Error accessing localStorage: {str(e)}")
    
    # Get cursor_email from cookies or use github_email as fallback
    for cookie in cookies:
        if cookie['name'] == 'cursor_email':
            cursor_email = cookie['value']
            print(f"{CHECK_MARK} Found cursor_email: {cursor_email}")
            break
    
    if not cursor_email and github_email:
        cursor_email = github_email
        print(f"{CHECK_MARK} Using GitHub email as fallback: {cursor_email}")
    
    if not auth_token or not cursor_email:
        missing = []
        if not auth_token:
            missing.append("auth_token")
        if not cursor_email:
            missing.append("cursor_email")
        print(f"{CROSS_MARK} Could not extract: {', '.join(missing)}")
        return None, None
    
    return auth_token, cursor_email

def reset_trial(translator=None):
    """Reset trial using GitHub authentication."""
    print(f"\n{Fore.CYAN}Starting GitHub trial reset...{Fore.RESET}")
    
    # Initialize browser
    page = ChromiumPage()
    
    try:
        # Get saved credentials
        email, password = get_saved_credentials()
        
        if not email or not password:
            print(f"{Fore.YELLOW}Please enter your GitHub credentials:{Fore.RESET}")
            email = input("Email: ")
            password = input("Password: ")
            
            # Save credentials if user wants
            save = input("Save credentials for next time? (y/n): ").lower() == 'y'
            if save:
                if save_credentials(email, password):
                    print(f"{CHECK_MARK} Credentials saved successfully")
                else:
                    print(f"{CROSS_MARK} Failed to save credentials")
        
        # Navigate to GitHub login
        print(f"\n{Fore.CYAN}Navigating to GitHub login...{Fore.RESET}")
        page.get('https://github.com/login')
        
        # Fill in login form
        page.ele('input[name="login"]').input(email)
        page.ele('input[name="password"]').input(password)
        page.ele('input[name="commit"]').click()
        
        # Wait for login to complete
        time.sleep(2)
        
        # Check if login was successful
        if 'login' in page.url:
            print(f"{CROSS_MARK} Login failed. Please check your credentials.")
            return False
        
        print(f"{CHECK_MARK} Successfully logged in to GitHub")
        
        # Extract authentication data
        auth_token, cursor_email = extract_auth_data(page, email)
        if not auth_token or not cursor_email:
            print(f"{CROSS_MARK} Could not extract authentication data")
            return False
        
        # Initialize CursorAuth and save authentication data
        cursor_auth = CursorAuth()
        cursor_auth.set_access_token(auth_token)
        cursor_auth.set_refresh_token(auth_token)  # Using same token for both
        cursor_auth.set_email(cursor_email)
        
        if not cursor_auth.verify_and_save():
            print(f"{CROSS_MARK} Failed to save authentication data")
            return False
        
        print(f"{CHECK_MARK} Successfully saved authentication data")
        
        # Reset machine ID
        print(f"\n{Fore.CYAN}Resetting machine ID...{Fore.RESET}")
        resetter = MachineIDResetter()
        resetter.reset()
        print(f"{CHECK_MARK} Machine ID reset complete")
        
        print(f"\n{Fore.GREEN}Trial reset complete! You can now launch Cursor.{Fore.RESET}")
        return True
        
    except Exception as e:
        print(f"{CROSS_MARK} An error occurred: {str(e)}")
        return False
        
    finally:
        page.quit() 