import os
import shutil
import platform
import time
import sys

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
    print("  • Removes custom extensions and preferences")
    print("  • Resets trial information and activation data")
    print("  • Helps resolve common issues with Cursor AI editor")
    print("  • Compatible with Windows, macOS, and Linux\n")

def display_disclaimer():
    """Displays a disclaimer for the user."""
    print("\n⚠️ DISCLAIMER:")
    print("  This tool will permanently delete all Cursor AI settings,")
    print("  extensions, and cached data. This action cannot be undone.")
    print("  Your code files will NOT be affected, but all editor")
    print("  preferences and AI history will be reset to default.")
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
    if os.path.exists(path):
        try:
            shutil.rmtree(path, ignore_errors=True)
            print(f"[✅] Deleted: {path}")
        except Exception as e:
            print(f"[❌] Error deleting {path}: {str(e)}")
    else:
        print(f"[ℹ️] Not Found: {path}")

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

    if system == "Windows":
        cursor_paths = [
            os.path.join(home, "AppData", "Roaming", "Cursor"),
            os.path.join(home, "AppData", "Local", "Cursor"),
            os.path.join(home, ".vscode"),  # Cursor sometimes stores extensions here
            os.path.join(home, "AppData", "Local", "Temp", "Cursor"),  # Temporary data
        ]

    elif system == "Darwin":  # macOS
        cursor_paths = [
            os.path.join(home, "Library", "Application Support", "Cursor"),
            os.path.join(home, "Library", "Caches", "Cursor"),
            os.path.join(home, "Library", "Preferences", "Cursor"),
            os.path.join(home, ".vscode"),  # Cursor sometimes stores extensions here
        ]

    elif system == "Linux":
        cursor_paths = [
            os.path.join(home, ".config", "Cursor"),
            os.path.join(home, ".cache", "Cursor"),
            os.path.join(home, ".local", "share", "Cursor"),
            os.path.join(home, ".vscode"),  # Cursor sometimes stores extensions here
        ]

    else:
        print("❌ Unsupported OS. Exiting.")
        return

    for path in cursor_paths:
        remove_dir(path)

    # Remove potential files that store trial/activation data
    cursor_trial_paths = [
        os.path.join(home, ".cursor_trial_data"),
        os.path.join(home, "AppData", "Local", "Cursor", "trial_info.json"),  # Windows
        os.path.join(home, "Library", "Application Support", "Cursor", "trial_info.json"),  # macOS
        os.path.join(home, ".config", "Cursor", "trial_info.json"),  # Linux
    ]

    print("\n🔄 Removing trial data and license information...\n")
    for path in cursor_trial_paths:
        if os.path.isfile(path):
            try:
                os.remove(path)
                print(f"[✅] Deleted file: {path}")
            except Exception as e:
                print(f"[❌] Error deleting file {path}: {str(e)}")
        else:
            remove_dir(path)  # In case it's a directory

    print("\n✅ Cursor AI has been fully reset! Restart your system for changes to take effect.")
    print("   You will need to reinstall and reconfigure Cursor AI.")
    print("   If you encounter any issues, contact Prathmesh </> on Discord: prathmesh_pro\n")

if __name__ == "__main__":
    try:
        reset_cursor()
    except KeyboardInterrupt:
        print("\n\n🛑 Process interrupted by user. Exiting...\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {str(e)}\n")
        sys.exit(1)
