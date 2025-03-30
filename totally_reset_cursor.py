        input(f"\n{Fore.CYAN}{EMOJI['INFO']} {translator.get('totally_reset.press_enter_to_return_to_main_menu')} {Style.RESET_ALL}")import os
import shutil
import platform
import sys
import uuid
import json
from datetime import datetime
from colorama import Fore, Style, init

# Initialize colorama
init()

# Define simplified emoji constants
EMOJI = {
    "SUCCESS": "✅",
    "ERROR": "❌",
    "INFO": "ℹ️",
    "RESET": "🔄",
    "WARNING": "⚠️"
}

def get_confirmation():
    """Gets confirmation from the user to proceed."""
    choice = input(f"{Fore.RED}{EMOJI['WARNING']} Confirm Cursor AI reset (y/n): ").strip().lower()
    return choice == "y" or choice == ""

def remove_path(path):
    """Removes a directory or file if it exists."""
    if not path or not os.path.exists(path):
        return
        
    try:
        if os.path.isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path, ignore_errors=True)
        print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Deleted: {path} {Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} Error deleting {path}: {str(e)} {Style.RESET_ALL}")

def create_fake_machine_id(path):
    """Creates a new machine ID file with random ID."""
    try:
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(path, 'w') as f:
            f.write(str(uuid.uuid4()))
        print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Created new machine ID: {path} {Style.RESET_ALL}")
    except Exception:
        pass

def create_fake_trial_info(path):
    """Creates fake trial information to extend trial period."""
    try:
        # Generate future expiry date (90 days from now)
        future_date = (datetime.now().timestamp() + (90 * 24 * 60 * 60)) * 1000  # milliseconds
        
        # Create fake trial info
        fake_trial = {
            "trialStartTimestamp": datetime.now().timestamp() * 1000,
            "trialEndTimestamp": future_date,
            "hasUsedTrial": False,
            "machineId": str(uuid.uuid4())
        }
        
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        with open(path, 'w') as f:
            json.dump(fake_trial, f)
        print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Created extended trial: {path} {Style.RESET_ALL}")
    except Exception:
        pass

def reset_cursor():
    """Reset Cursor AI by removing settings, caches, and creating new identifiers."""
    system = platform.system()
    home = os.path.expanduser("~")

    print(f"\n{Fore.CYAN}====== Cursor AI Reset Tool ======{Style.RESET_ALL}")
    print(f"{Fore.RED}{EMOJI['WARNING']} This will reset Cursor AI completely:")
    print(f"• All settings, cache, and identifiers will be removed")
    print(f"• Data may be unrecoverable")
    print(f"• You may need to reinstall Cursor after reset{Style.RESET_ALL}\n")
    
    if not get_confirmation():
        print(f"\n{Fore.CYAN}Reset cancelled.{Style.RESET_ALL}")
        return

    print(f"\n{Fore.CYAN}{EMOJI['RESET']} Resetting Cursor AI...{Style.RESET_ALL}")

    # Define paths based on OS
    cursor_paths = []
    machine_id_paths = []
    trial_info_path = ""
    
    if system == "Windows":
        cursor_paths = [
            os.path.join(home, "AppData", "Roaming", "Cursor"),
            os.path.join(home, "AppData", "Local", "Cursor"),
            os.path.join(home, "AppData", "Roaming", "cursor-electron"),
            os.path.join(home, "AppData", "Local", "cursor-electron"),
            os.path.join(home, "AppData", "Local", "CursorAI"),
            os.path.join(home, "AppData", "Roaming", "CursorAI"),
            os.path.join(home, "AppData", "Local", "Temp", "Cursor"),
            os.path.join(home, "AppData", "Local", "Temp", "cursor-updater"),
            os.path.join(home, ".cursor_trial_data"),
            os.path.join(home, ".cursor_license"),
            os.path.join(home, ".cursor-machine-id"),
            os.path.join(home, ".cursor-state.json"),
        ]
        machine_id_paths = [
            os.path.join(home, "AppData", "Roaming", "Cursor", "cursor-machine-id"),
            os.path.join(home, "AppData", "Local", "Cursor", "cursor-machine-id"),
        ]
        trial_info_path = os.path.join(home, "AppData", "Roaming", "Cursor", "trial_info.json")
        
    elif system == "Darwin":  # macOS
        cursor_paths = [
            os.path.join(home, "Library", "Application Support", "Cursor"),
            os.path.join(home, "Library", "Application Support", "cursor-electron"),
            os.path.join(home, "Library", "Caches", "Cursor"),
            os.path.join(home, "Library", "Caches", "cursor-electron"),
            os.path.join(home, "Library", "Preferences", "Cursor"),
            os.path.join(home, "Library", "Preferences", "cursor-electron"),
            os.path.join(home, "Library", "Saved Application State", "com.cursor.Cursor.savedState"),
            os.path.join(home, "Library", "HTTPStorages", "com.cursor.Cursor"),
            os.path.join(home, ".cursor_trial_data"),
            os.path.join(home, ".cursor_license"),
            os.path.join(home, ".cursor-machine-id"),
        ]
        machine_id_paths = [
            os.path.join(home, "Library", "Application Support", "Cursor", "cursor-machine-id"),
        ]
        trial_info_path = os.path.join(home, "Library", "Application Support", "Cursor", "trial_info.json")
        
    elif system == "Linux":
        cursor_paths = [
            os.path.join(home, ".config", "Cursor"),
            os.path.join(home, ".config", "cursor-electron"),
            os.path.join(home, ".cache", "Cursor"),
            os.path.join(home, ".cache", "cursor-electron"),
            os.path.join(home, ".local", "share", "Cursor"),
            os.path.join(home, ".local", "share", "cursor-electron"),
            os.path.join(home, ".cursor_trial_data"),
            os.path.join(home, ".cursor_license"),
            os.path.join(home, ".cursor-machine-id"),
        ]
        machine_id_paths = [
            os.path.join(home, ".config", "Cursor", "cursor-machine-id"),
        ]
        trial_info_path = os.path.join(home, ".config", "Cursor", "trial_info.json")
    else:
        print(f"{Fore.RED}{EMOJI['ERROR']} Unsupported OS: {system} {Style.RESET_ALL}")
        return

    # Remove main Cursor directories and files
    for path in cursor_paths:
        remove_path(path)

    # Create new machine IDs
    print(f"\n{Fore.CYAN}{EMOJI['RESET']} Creating new machine identifiers...{Style.RESET_ALL}")
    for path in machine_id_paths:
        create_fake_machine_id(path)

    # Create new trial with extended expiration
    print(f"\n{Fore.CYAN}{EMOJI['RESET']} Creating new trial information...{Style.RESET_ALL}")
    create_fake_trial_info(trial_info_path)

    print(f"\n{Fore.GREEN}{EMOJI['SUCCESS']} Cursor AI has been reset successfully!")
    print(f"{Fore.CYAN}{EMOJI['INFO']} Reinstall Cursor if needed and enjoy your extended trial.{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        reset_cursor()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.RED}{EMOJI['WARNING']} Process interrupted.{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}{EMOJI['ERROR']} Unexpected error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)
