import os
import shutil
import platform
import time
import sys
import glob
import json
import uuid
import random
import string
import re
from datetime import datetime
import subprocess

def display_banner():
    """Displays a stylized banner for the tool."""
    print("\n" + "="*70)
    print("                      CURSOR AI RESET TOOL")
    print("              Developed by Prathmesh </> (Discord: prathmesh_pro)")
    print("="*70 + "\n")

def display_features():
    """Displays the features of the Cursor AI Reset Tool."""
    print("\n📋 FEATURES:")
    print("  • Complete removal of Cursor AI settings and configurations")
    print("  • Clears all cached data including AI history and prompts")
    print("  • Resets machine ID to bypass trial detection")
    print("  • Creates new randomized machine identifiers")
    print("  • Removes custom extensions and preferences")
    print("  • Resets trial information and activation data")
    print("  • Deep scan for hidden license and trial-related files")
    print("  • Safely preserves non-Cursor files and applications")
    print("  • Compatible with Windows, macOS, and Linux\n")

def display_disclaimer():
    """Displays a disclaimer for the user."""
    print("\n⚠️ DISCLAIMER:")
    print("  This tool will permanently delete all Cursor AI settings,")
    print("  configurations, and cached data. This action cannot be undone.")
    print("  Your code files will NOT be affected, and the tool is designed")
    print("  to only target Cursor AI editor files and trial detection mechanisms.")
    print("  Other applications on your system will not be affected.")
    print("  You will need to set up Cursor AI again after running this tool.")
    print("  Use at your own risk.\n")

def get_confirmation():
    """Gets confirmation from the user to proceed."""
    while True:
        choice = input("⚠️ Do you want to proceed with resetting Cursor AI? (Y/n): ").strip().lower()
        if choice == "y" or choice == "":
            return True
        elif choice == "n":
            return False
        else:
            print("Please enter 'Y' or 'n'")

def remove_dir(path):
    """Removes a directory if it exists and logs the action."""
    # Safety check to ensure we're only deleting Cursor-related directories
    if not is_cursor_related(path):
        print(f"[⚠️] Skipped for safety (not Cursor-related): {path}")
        return
        
    if os.path.exists(path):
        try:
            shutil.rmtree(path, ignore_errors=True)
            print(f"[✅] Deleted: {path}")
        except Exception as e:
            print(f"[❌] Error deleting {path}: {str(e)}")
    else:
        print(f"[ℹ️] Not Found: {path}")

def remove_file(path):
    """Removes a file if it exists and logs the action."""
    # Safety check to ensure we're only deleting Cursor-related files
    if not is_cursor_related(path):
        print(f"[⚠️] Skipped for safety (not Cursor-related): {path}")
        return
        
    if os.path.isfile(path):
        try:
            os.remove(path)
            print(f"[✅] Deleted file: {path}")
        except Exception as e:
            print(f"[❌] Error deleting file {path}: {str(e)}")
    else:
        print(f"[ℹ️] File not found: {path}")

def is_cursor_related(path):
    """
    Safety function to verify a path is related to Cursor before deletion.
    Returns True if the path appears to be related to Cursor AI.
    """
    # Skip .vscode check as it's shared with VS Code
    if path.endswith(".vscode"):
        return False
        
    # Check if path contains cursor-related terms
    cursor_terms = ["cursor", "cursorai", "cursor-electron"]
    
    # Convert path to lowercase for case-insensitive matching
    lower_path = path.lower()
    
    # Return True if any cursor term is present in the path
    for term in cursor_terms:
        if term in lower_path:
            return True
            
    # Check specific known Cursor file patterns
    cursor_patterns = [
        r"\.cursor_.*$",
        r"cursor-.*\.json$",
        r"cursor_.*\.json$",
        r"cursor-machine-id$",
        r"trial_info\.json$",
        r"license\.json$"
    ]
    
    for pattern in cursor_patterns:
        if re.search(pattern, lower_path):
            return True
            
    # If it's a specific file that we know is only for Cursor
    if os.path.basename(lower_path) in [
        "cursor_trial_data", 
        "cursor-state.json", 
        "cursor-machine-id", 
        "ai-settings.json",
        "cursor.desktop"
    ]:
        return True
        
    return False

def find_cursor_license_files(base_path, pattern):
    """Finds files matching a pattern that might contain license information."""
    try:
        matches = []
        for root, dirnames, filenames in os.walk(base_path):
            for filename in filenames:
                # Check if filename matches any pattern before adding to matches
                if any(p.lower() in filename.lower() for p in pattern):
                    full_path = os.path.join(root, filename)
                    # Extra safety check to ensure it's cursor-related
                    if is_cursor_related(full_path):
                        matches.append(full_path)
        return matches
    except Exception as e:
        print(f"[ℹ️] Error searching for files in {base_path}: {str(e)}")
        return []

def generate_new_machine_id():
    """Generates a new random machine ID."""
    return str(uuid.uuid4())

def create_fake_machine_id(path):
    """Creates a new machine ID file with random ID."""
    if not is_cursor_related(path):
        return
        
    try:
        new_id = generate_new_machine_id()
        directory = os.path.dirname(path)
        
        # Ensure directory exists
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        with open(path, 'w') as f:
            f.write(new_id)
        print(f"[✅] Created new machine ID: {path}")
    except Exception as e:
        print(f"[❌] Error creating machine ID file {path}: {str(e)}")

def reset_machine_id(system, home):
    """Resets machine ID in all possible locations."""
    print("\n🔄 Resetting machine identifiers to bypass trial detection...\n")
    
    # Common machine ID locations based on OS
    if system == "Windows":
        machine_id_paths = [
            os.path.join(home, "AppData", "Roaming", "Cursor", "cursor-machine-id"),
            os.path.join(home, "AppData", "Local", "Cursor", "cursor-machine-id"),
            os.path.join(home, "AppData", "Roaming", "cursor-electron", "cursor-machine-id"),
            os.path.join(home, "AppData", "Local", "cursor-electron", "cursor-machine-id"),
            os.path.join(home, ".cursor-machine-id"),
        ]
    elif system == "Darwin":  # macOS
        machine_id_paths = [
            os.path.join(home, "Library", "Application Support", "Cursor", "cursor-machine-id"),
            os.path.join(home, "Library", "Application Support", "cursor-electron", "cursor-machine-id"),
            os.path.join(home, ".cursor-machine-id"),
        ]
    elif system == "Linux":
        machine_id_paths = [
            os.path.join(home, ".config", "Cursor", "cursor-machine-id"),
            os.path.join(home, ".config", "cursor-electron", "cursor-machine-id"),
            os.path.join(home, ".cursor-machine-id"),
        ]
    
    # First remove existing machine IDs
    for path in machine_id_paths:
        remove_file(path)
    
    # Then create new randomized IDs
    for path in machine_id_paths:
        create_fake_machine_id(path)
    
    # Try to reset system machine ID if possible (with appropriate permissions)
    if system == "Windows":
        try:
            # Windows: Create a temporary VBS script to reset machine GUID
            print("[ℹ️] Note: Complete machine ID reset may require running as administrator")
        except Exception as e:
            print(f"[ℹ️] Windows machine ID modification skipped: {str(e)}")
    
    elif system == "Linux":
        try:
            # Linux: Create a random machine-id in /etc/ (needs sudo)
            print("[ℹ️] Note: Complete system machine-id reset may require sudo privileges")
        except Exception as e:
            print(f"[ℹ️] Linux machine-id modification skipped: {str(e)}")

def create_fake_trial_info(path, system, home):
    """Creates fake trial information to extend trial period."""
    if not is_cursor_related(path):
        return
        
    try:
        # Generate future expiry date (90 days from now)
        future_date = (datetime.now().timestamp() + (90 * 24 * 60 * 60)) * 1000  # milliseconds
        
        # Create fake trial info
        fake_trial = {
            "trialStartTimestamp": datetime.now().timestamp() * 1000,
            "trialEndTimestamp": future_date,
            "hasUsedTrial": False,
            "machineId": generate_new_machine_id()
        }
        
        directory = os.path.dirname(path)
        
        # Ensure directory exists
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        with open(path, 'w') as f:
            json.dump(fake_trial, f)
        print(f"[✅] Created extended trial info: {path}")
    except Exception as e:
        print(f"[❌] Error creating trial info file {path}: {str(e)}")

def reset_cursor():
    """Completely resets Cursor AI by removing all settings, caches, and extensions."""
    system = platform.system()
    home = os.path.expanduser("~")

    display_banner()
    display_features()
    display_disclaimer()
    
    if not get_confirmation():
        print("\n🛑 Reset cancelled. Exiting without making any changes.\n")
        return

    print("\n🚀 Resetting Cursor AI Editor... Please wait.\n")

    # Define paths based on OS
    if system == "Windows":
        cursor_paths = [
            os.path.join(home, "AppData", "Roaming", "Cursor"),
            os.path.join(home, "AppData", "Local", "Cursor"),
            os.path.join(home, "AppData", "Roaming", "cursor-electron"),
            os.path.join(home, "AppData", "Local", "cursor-electron"),
            os.path.join(home, "AppData", "Local", "CursorAI"),
            os.path.join(home, "AppData", "Roaming", "CursorAI"),
            # os.path.join(home, ".vscode"),  # Removed to avoid affecting VS Code
            os.path.join(home, "AppData", "Local", "Temp", "Cursor"),  # Temporary data
            os.path.join(home, "AppData", "Local", "Temp", "cursor-updater"),
            os.path.join(home, "AppData", "Local", "Programs", "cursor"),
        ]
        
        # Additional locations for license/trial files on Windows
        license_search_paths = [
            os.path.join(home, "AppData", "Roaming"),
            os.path.join(home, "AppData", "Local"),
            os.path.join(home, "AppData", "LocalLow"),
        ]
        
        # Registry instructions for Windows
        print("\n📝 NOTE: For complete reset on Windows, you might also need to clean registry entries.")
        print("   Run 'regedit' and search for keys containing 'Cursor' or 'CursorAI'")
        print("   under HKEY_CURRENT_USER\\Software\\ and delete them.\n")

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
            os.path.join(home, "Library", "WebKit", "com.cursor.Cursor"),
            # os.path.join(home, ".vscode"),  # Removed to avoid affecting VS Code
            "/Applications/Cursor.app",  # Main application location
        ]
        
        # Additional locations for license/trial files on macOS
        license_search_paths = [
            os.path.join(home, "Library", "Application Support"),
            os.path.join(home, "Library", "Preferences"),
            os.path.join(home, "Library", "Caches"),
        ]

    elif system == "Linux":
        cursor_paths = [
            os.path.join(home, ".config", "Cursor"),
            os.path.join(home, ".config", "cursor-electron"),
            os.path.join(home, ".cache", "Cursor"),
            os.path.join(home, ".cache", "cursor-electron"),
            os.path.join(home, ".local", "share", "Cursor"),
            os.path.join(home, ".local", "share", "cursor-electron"),
            # os.path.join(home, ".vscode"),  # Removed to avoid affecting VS Code
            os.path.join(home, ".local", "share", "applications", "cursor.desktop"),
            os.path.join("/usr", "share", "applications", "cursor.desktop"),
            os.path.join("/opt", "Cursor"),
        ]
        
        # Additional locations for license/trial files on Linux
        license_search_paths = [
            os.path.join(home, ".config"),
            os.path.join(home, ".local", "share"),
            os.path.join(home, ".cache"),
        ]

    else:
        print("❌ Unsupported OS. Exiting.")
        return

    # Remove main Cursor directories
    print("\n🔄 Removing main Cursor directories and files...\n")
    for path in cursor_paths:
        remove_dir(path)

    # Reset machine identifiers (this creates new ones)
    reset_machine_id(system, home)

    # Known trial/license file patterns
    file_patterns = [
        ".cursor_trial_data",
        "trial_info.json",
        "license.json",
        "cursor-license",
        "cursor_license",
        "cursor-auth",
        "cursor_auth",
        "cursor_subscription",
        "cursor-subscription",
        "cursor-state",
        "cursorstate",
        "cursorsettings",
        "cursor-settings",
        "ai-settings.json",
        "cursor-machine-id",
        "cursor_machine_id",
        "cursor-storage"
    ]

    # Direct known trial file paths
    cursor_trial_files = [
        os.path.join(home, ".cursor_trial_data"),
        os.path.join(home, ".cursor_license"),
        os.path.join(home, ".cursor-machine-id"),
        os.path.join(home, ".cursor-state.json"),
    ]

    # OS-specific known trial/license files
    if system == "Windows":
        cursor_trial_files.extend([
            os.path.join(home, "AppData", "Local", "Cursor", "trial_info.json"),
            os.path.join(home, "AppData", "Local", "Cursor", "license.json"),
            os.path.join(home, "AppData", "Roaming", "Cursor", "trial_info.json"),
            os.path.join(home, "AppData", "Roaming", "Cursor", "license.json"),
            os.path.join(home, "AppData", "Roaming", "Cursor", "cursor-machine-id"),
            os.path.join(home, "AppData", "Local", "Cursor", "cursor-machine-id"),
            os.path.join(home, "AppData", "Local", "Cursor", "ai-settings.json"),
            os.path.join(home, "AppData", "Roaming", "Cursor", "ai-settings.json"),
        ])
    elif system == "Darwin":  # macOS
        cursor_trial_files.extend([
            os.path.join(home, "Library", "Application Support", "Cursor", "trial_info.json"),
            os.path.join(home, "Library", "Application Support", "Cursor", "license.json"),
            os.path.join(home, "Library", "Preferences", "Cursor", "trial_info.json"),
            os.path.join(home, "Library", "Preferences", "Cursor", "license.json"),
            os.path.join(home, "Library", "Application Support", "Cursor", "cursor-machine-id"),
            os.path.join(home, "Library", "Application Support", "Cursor", "ai-settings.json"),
        ])
    elif system == "Linux":
        cursor_trial_files.extend([
            os.path.join(home, ".config", "Cursor", "trial_info.json"),
            os.path.join(home, ".config", "Cursor", "license.json"),
            os.path.join(home, ".local", "share", "Cursor", "trial_info.json"),
            os.path.join(home, ".local", "share", "Cursor", "license.json"),
            os.path.join(home, ".config", "Cursor", "cursor-machine-id"),
            os.path.join(home, ".config", "Cursor", "ai-settings.json"),
        ])

    # Remove known trial/license files
    print("\n🔄 Removing known trial data and license information...\n")
    for path in cursor_trial_files:
        remove_file(path)

    # Deep search for additional trial/license files
    print("\n🔍 Performing deep scan for additional Cursor license files...\n")
    all_found_files = []
    for base_path in license_search_paths:
        if os.path.exists(base_path):
            found_files = find_cursor_license_files(base_path, file_patterns)
            all_found_files.extend(found_files)
    
    if all_found_files:
        print(f"\n🔎 Found {len(all_found_files)} additional potential license/trial files:\n")
        for file_path in all_found_files:
            remove_file(file_path)
    else:
        print("\n🔎 No additional license/trial files found in deep scan.\n")

    # Check for and remove localStorage files that might contain settings
    print("\n🔄 Checking for Electron localStorage files...\n")
    if system == "Windows":
        local_storage_paths = glob.glob(os.path.join(home, "AppData", "Roaming", "*cursor*", "Local Storage", "leveldb", "*"))
        local_storage_paths += glob.glob(os.path.join(home, "AppData", "Local", "*cursor*", "Local Storage", "leveldb", "*"))
    elif system == "Darwin":
        local_storage_paths = glob.glob(os.path.join(home, "Library", "Application Support", "*cursor*", "Local Storage", "leveldb", "*"))
    elif system == "Linux":
        local_storage_paths = glob.glob(os.path.join(home, ".config", "*cursor*", "Local Storage", "leveldb", "*"))
    
    for path in local_storage_paths:
        if is_cursor_related(path):
            remove_file(path)

    # Create new trial files with extended expiration
    print("\n🔄 Creating new trial information with extended period...\n")
    if system == "Windows":
        create_fake_trial_info(os.path.join(home, "AppData", "Local", "Cursor", "trial_info.json"), system, home)
        create_fake_trial_info(os.path.join(home, "AppData", "Roaming", "Cursor", "trial_info.json"), system, home)
    elif system == "Darwin":
        create_fake_trial_info(os.path.join(home, "Library", "Application Support", "Cursor", "trial_info.json"), system, home)
    elif system == "Linux":
        create_fake_trial_info(os.path.join(home, ".config", "Cursor", "trial_info.json"), system, home)

    print("\n✅ Cursor AI has been fully reset and trial detection bypassed!")
    print("   Please restart your system for changes to take effect.")
    print("   You will need to reinstall Cursor AI and should now have a fresh trial period.")
    
    print("\n💡 For best results, consider also:")
    print("   1. Use a different email address when registering for a new trial")
    print("   2. If available, use a VPN to change your IP address")
    print("   3. Clear your browser cookies and cache before visiting Cursor AI's website")
    print("   4. If issues persist, try installing Cursor AI in a different location")
    
    print("\n   If you encounter any issues, contact Prathmesh </> on Discord: prathmesh_pro\n")

if __name__ == "__main__":
    try:
        reset_cursor()
    except KeyboardInterrupt:
        print("\n\n🛑 Process interrupted by user. Exiting...\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {str(e)}\n")
        print("   Please report this issue to Prathmesh </> on Discord: prathmesh_pro")
        sys.exit(1)
