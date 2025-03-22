import os
import time
import uuid
import json
import random
import string
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def generate_temp_email():
    """Generates a temporary email using 1secmail API."""
    try:
        response = requests.get("https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1")
        response.raise_for_status()
        email = response.json()[0]
        logging.info(f"Generated temp email: {email}")
        return email
    except requests.RequestException as e:
        logging.error(f"Failed to generate temp email: {e}")
        raise

def extract_inbox(email, retries=5, wait_time=10):
    """Extracts the inbox for the temp email with retries."""
    domain = email.split('@')[1]
    login = email.split('@')[0]
    inbox_url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}"
    
    for attempt in range(retries):
        time.sleep(wait_time)
        try:
            messages = requests.get(inbox_url).json()
            if messages:
                logging.info(f"Inbox found on attempt {attempt + 1}: {messages[0]['id']}")
                return messages[0]['id']
            logging.info(f"Retry {attempt + 1}/{retries}: No email yet...")
        except requests.RequestException as e:
            logging.error(f"Error fetching inbox: {e}")
    logging.warning("No messages found after retries.")
    return None

def get_verification_link(email, message_id):
    """Retrieves the verification link from the email inbox."""
    domain = email.split('@')[1]
    login = email.split('@')[0]
    msg_url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={login}&domain={domain}&id={message_id}"
    try:
        message = requests.get(msg_url).json()
        for line in message['body'].splitlines():
            if "https://github.com/" in line:
                logging.info(f"Verification link found: {line}")
                return line.strip()
        logging.warning("Verification link not found in email.")
        return None
    except requests.RequestException as e:
        logging.error(f"Failed to fetch email message: {e}")
        return None

def reset_machine_id():
    """Resets the machine ID to bypass trial detection."""
    new_id = str(uuid.uuid4())
    try:
        if os.name == 'nt':  # Windows
            os.system(f'reg add "HKLM\\SOFTWARE\\Microsoft\\Cryptography" /v MachineGuid /d {new_id} /f')
            logging.info(f"Machine ID reset on Windows: {new_id}")
        elif os.name == 'posix':  # Linux/macOS
            if os.path.exists("/etc/machine-id"):
                os.system(f'echo {new_id} | sudo tee /etc/machine-id')
                logging.info(f"Machine ID reset on Linux: {new_id}")
            else:
                logging.info("Machine ID reset skipped (macOS or no /etc/machine-id)")
        else:
            logging.warning("Unsupported OS for machine ID reset.")
    except Exception as e:
        logging.error(f"Failed to reset machine ID: {e}")

def register_github(email):
    """Automates GitHub registration with temp email."""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get("https://github.com/join")

        # Generate random credentials
        username = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=15))

        # Fill in the registration form
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "user_login")))
        driver.find_element(By.ID, "user_login").send_keys(username)
        driver.find_element(By.ID, "user_email").send_keys(email)
        driver.find_element(By.ID, "user_password").send_keys(password)
        driver.find_element(By.ID, "signup_button").click()

        # Wait for page transition (GitHub might redirect or show CAPTCHA)
        time.sleep(5)
        logging.info(f"GitHub account created: {username} | {email}")
        return username, password
    except Exception as e:
        logging.error(f"GitHub registration failed: {e}")
        raise
    finally:
        if driver:
            driver.quit()

def register_cursor_with_github(github_username, github_password):
    """Logs into Cursor AI using GitHub authentication."""
    options = Options()
    options.add_argument('--headless')
    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get("https://cursor.sh")
        
        # Sign in with GitHub
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Sign in with GitHub')]")))
        driver.find_element(By.XPATH, "//a[contains(text(), 'Sign in with GitHub')]").click()

        # GitHub login page
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "login_field")))
        driver.find_element(By.ID, "login_field").send_keys(github_username)
        driver.find_element(By.ID, "password").send_keys(github_password)
        driver.find_element(By.NAME, "commit").click()

        time.sleep(5)  # Wait for login to complete
        logging.info("Registered Cursor with GitHub")
    except Exception as e:
        logging.error(f"Cursor registration failed: {e}")
        raise
    finally:
        if driver:
            driver.quit()

def save_credentials(email, github_username, github_password):
    """Saves the credentials in a log file."""
    try:
        with open("github_cursor_accounts.txt", "a") as f:
            f.write(json.dumps({
                "email": email,
                "github_username": github_username,
                "github_password": github_password,
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            }) + "\n")
        logging.info("Credentials saved to github_cursor_accounts.txt")
    except Exception as e:
        logging.error(f"Failed to save credentials: {e}")

def display_features_and_warnings():
    """Displays features and warnings before proceeding."""
    print("\n🚀 GitHub + Cursor AI Registration Automation")
    print("=====================================")
    print("Features:")
    print("  - Generates a temporary email using 1secmail.")
    print("  - Registers a new GitHub account with random credentials.")
    print("  - Verifies the GitHub email automatically.")
    print("  - Logs into Cursor AI using GitHub authentication.")
    print("  - Resets the machine ID to bypass trial detection.")
    print("  - Saves all credentials to a file.")
    print("\n⚠️ Warnings:")
    print("  - This script automates account creation, which may violate GitHub/Cursor terms of service.")
    print("  - Requires internet access and administrative privileges.")
    print("  - CAPTCHA or additional verification may interrupt automation.")
    print("  - Use responsibly and at your own risk.")
    print("=====================================\n")

def get_user_confirmation():
    """Prompts the user for confirmation to proceed."""
    while True:
        response = input("Do you want to proceed with GitHub + Cursor AI registration? (yes/no): ").lower().strip()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        else:
            print("Please enter 'yes' or 'no'.")

def main(translator=None):
    logging.info("Starting GitHub + Cursor AI Registration Automation")
    
    # 如果没有提供translator，使用默认英文提示
    if translator is None:
        # Display features and warnings in English
        display_features_and_warnings()
        
        if not get_user_confirmation():
            logging.info("Operation cancelled by user.")
            print("❌ Operation cancelled.")
            return
    else:
        # 使用translator显示多语言提示
        print(f"\n🚀 {translator.get('github_register.title')}")
        print("=====================================")
        print(f"{translator.get('github_register.features_header')}:")
        print(f"  - {translator.get('github_register.feature1')}")
        print(f"  - {translator.get('github_register.feature2')}")
        print(f"  - {translator.get('github_register.feature3')}")
        print(f"  - {translator.get('github_register.feature4')}")
        print(f"  - {translator.get('github_register.feature5')}")
        print(f"  - {translator.get('github_register.feature6')}")
        print(f"\n⚠️ {translator.get('github_register.warnings_header')}:")
        print(f"  - {translator.get('github_register.warning1')}")
        print(f"  - {translator.get('github_register.warning2')}")
        print(f"  - {translator.get('github_register.warning3')}")
        print(f"  - {translator.get('github_register.warning4')}")
        print("=====================================\n")
        
        while True:
            response = input(f"{translator.get('github_register.confirm')} (yes/no): ").lower().strip()
            if response in ['yes', 'y']:
                break
            elif response in ['no', 'n']:
                print(f"❌ {translator.get('github_register.cancelled')}")
                return
            else:
                print(f"{translator.get('github_register.invalid_choice')}")

    try:
        # Step 1: Generate temp email
        email = generate_temp_email()

        # Step 2: Register GitHub account
        github_username, github_password = register_github(email)

        # Step 3: Extract and verify email
        inbox_id = extract_inbox(email)
        if inbox_id:
            verify_link = get_verification_link(email, inbox_id)
            if verify_link:
                options = Options()
                options.add_argument('--headless')
                driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
                try:
                    driver.get(verify_link)
                    logging.info("GitHub email verified")
                finally:
                    driver.quit()
            else:
                logging.error("Verification link not found")
                return
        else:
            logging.error("Email verification failed")
            return

        # Step 4: Register Cursor with GitHub
        register_cursor_with_github(github_username, github_password)

        # Step 5: Reset Machine ID
        reset_machine_id()

        # Step 6: Save credentials
        save_credentials(email, github_username, github_password)

        logging.info("All steps completed successfully!")
        print("✅ All steps completed!")
    except Exception as e:
        logging.error(f"Script failed: {e}")
        print(f"❌ An error occurred: {e}")

if __name__ == '__main__':
    main()
