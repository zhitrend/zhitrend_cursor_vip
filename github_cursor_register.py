import os
import time
import uuid
import json
import random
import string
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

def generate_temp_email():
    """Generates a temporary email and returns the email and inbox ID."""
    response = requests.get("https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1")
    email = response.json()[0]
    print(f"✅ Generated temp email: {email}")
    return email

def extract_inbox(email):
    """Extracts the inbox for the temp email."""
    domain = email.split('@')[1]
    login = email.split('@')[0]
    inbox_url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}"
    time.sleep(10)  # Allow email to arrive
    messages = requests.get(inbox_url).json()
    if messages:
        return messages[0]['id']
    return None

def get_verification_link(email, message_id):
    """Retrieves the verification link from the email inbox."""
    domain = email.split('@')[1]
    login = email.split('@')[0]
    msg_url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={login}&domain={domain}&id={message_id}"
    message = requests.get(msg_url).json()
    for line in message['body'].splitlines():
        if "https://github.com/" in line:
            print(f"✅ Verification link found: {line}")
            return line.strip()
    return None

def reset_machine_id():
    """Resets the machine ID to bypass Cursor AI's free trial detection."""
    new_id = str(uuid.uuid4())
    if os.name == 'nt':  # Windows
        os.system(f'reg add "HKLM\SOFTWARE\Microsoft\Cryptography" /v MachineGuid /d {new_id} /f')
    else:  # Linux/macOS
        os.system(f'echo {new_id} | sudo tee /etc/machine-id')
    print(f"✅ Machine ID reset: {new_id}")

def register_github(email):
    """Automates GitHub registration with temp email."""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://github.com/join")

    # Fill in the registration form
    username = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

    driver.find_element(By.ID, "user_login").send_keys(username)
    driver.find_element(By.ID, "user_email").send_keys(email)
    driver.find_element(By.ID, "user_password").send_keys(password)
    driver.find_element(By.ID, "signup_button").click()

    time.sleep(5)
    driver.quit()

    print(f"✅ GitHub account created: {username} | {email}")
    return username, password

def register_cursor_with_github(driver):
    """Logs into Cursor AI using GitHub authentication."""
    driver.get("https://cursor.sh")
    driver.find_element(By.LINK_TEXT, "Sign in with GitHub").click()
    time.sleep(5)
    print("✅ Registered Cursor with GitHub")

def main():
    print("\n🚀 Automating GitHub + Cursor AI Registration...\n")
    
    email = generate_temp_email()
    github_username, github_password = register_github(email)

    inbox_id = extract_inbox(email)
    if inbox_id:
        verify_link = get_verification_link(email, inbox_id)
        if verify_link:
            options = Options()
            options.add_argument('--headless')
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            driver.get(verify_link)
            print("✅ Verified GitHub Email")
            driver.quit()
        else:
            print("❌ Verification link not found")
    
    # Automate Cursor AI registration with GitHub
    options = Options()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    register_cursor_with_github(driver)

    # Reset Machine ID
    reset_machine_id()
    
    # Save credentials
    with open("github_cursor_accounts.txt", "a") as f:
        f.write(json.dumps({
            "email": email,
            "github_username": github_username,
            "github_password": github_password
        }) + "\n")
    
    print("✅ All steps completed!")

if __name__ == '__main__':
    main()
