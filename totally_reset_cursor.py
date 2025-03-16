import os
import shutil
import platform
import time

def remove_dir(path):
    """Removes a directory if it exists and logs the action."""
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)
        print(f"[✔] Deleted: {path}")
    else:
        print(f"[✘] Not Found: {path}")

def reset_cursor():
    """Completely resets Cursor AI by removing all settings, caches, and extensions."""
    system = platform.system()
    home = os.path.expanduser("~")

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
        remove_dir(path)

    print("\n✅ Cursor AI has been fully reset! Restart your system for changes to take effect.\n")

if __name__ == "__main__":
    reset_cursor()

