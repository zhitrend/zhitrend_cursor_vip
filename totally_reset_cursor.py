import os
import shutil
import platform
import time
import uuid
import subprocess

def delete_directory(path):
    """Deletes a directory and all its contents."""
    if os.path.exists(path):
        try:
            shutil.rmtree(path)
            print(f"✅ Removed: {path}")
        except Exception as e:
            print(f"❌ Failed to remove: {path} -> {e}")
    else:
        print(f"🔍 Not found: {path}")

def delete_file(path):
    """Deletes a file if it exists."""
    if os.path.isfile(path):
        try:
            os.remove(path)
            print(f"✅ Removed file: {path}")
        except Exception as e:
            print(f"❌ Failed to remove file: {path} -> {e}")
    else:
        print(f"🔍 Not found: {path}")

def reset_machine_id():
    """Resets the machine ID to a new UUID."""
    new_id = str(uuid.uuid4())
    if platform.system() == "Windows":
        try:
            subprocess.run(
                ["reg", "add", "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Cryptography", "/v", "MachineGuid", "/d", new_id, "/f"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print(f"✅ MachineGuid reset to: {new_id}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to reset MachineGuid: {e}")
    elif platform.system() == "Linux":
        machine_id_paths = ["/etc/machine-id", "/var/lib/dbus/machine-id"]
        for path in machine_id_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'w') as f:
                        f.write(new_id)
                    print(f"✅ Reset machine ID at: {path}")
                except Exception as e:
                    print(f"❌ Failed to reset machine ID at {path}: {e}")
    elif platform.system() == "Darwin":  # macOS
        print("ℹ️ macOS does not use a machine-id file. Skipping machine ID reset.")
    else:
        print("❌ Unsupported operating system for machine ID reset.")

def display_features_and_warnings():
    """Displays features and warnings before proceeding."""
    print("\n🚀 Cursor AI Reset Script")
    print("=====================================")
    print("Features:")
    print("  - Removes Cursor AI configuration directories and files.")
    print("  - Cleans up cache, preferences, and application data.")
    print("  - Performs a deep scan for hidden Cursor-related files.")
    print("  - Resets the machine ID to a new UUID (where applicable).")
    print("  - Supports Windows, Linux, and macOS.")
    print("\n⚠️ Warnings:")
    print("  - This action is IRREVERSIBLE. All Cursor AI data will be deleted.")
    print("  - Requires administrative privileges for some operations (e.g., machine ID reset on Windows/Linux).")
    print("  - May disrupt Cursor AI functionality until reinstalled or reconfigured.")
    print("  - Backup any important Cursor data before proceeding.")
    print("=====================================\n")

def get_user_confirmation():
    """Prompts the user for confirmation to proceed."""
    while True:
        response = input("Do you want to proceed with resetting Cursor AI? (yes/no): ").lower().strip()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        else:
            print("Please enter 'yes' or 'no'.")

def reset_cursor():
    print("\n🚀 Resetting Cursor AI...\n")

    # Platform-specific paths
    paths = []
    if platform.system() == "Linux":
        paths = [
            os.path.expanduser("~/.cursor"),
            os.path.expanduser("~/.local/share/cursor"),
            os.path.expanduser("~/.config/cursor"),
            os.path.expanduser("~/.cache/cursor"),
            "/usr/local/bin/cursor",
            "/opt/cursor",
            "/usr/bin/cursor",
            os.path.expanduser("~/.cursor/machine-id.db"),
            os.path.expanduser("~/.local/share/Cursor"),
            os.path.expanduser("~/.config/Cursor"),
            os.path.expanduser("~/.cache/Cursor")
        ]
    elif platform.system() == "Darwin":  # macOS
        paths = [
            os.path.expanduser("~/Library/Application Support/Cursor"),
            os.path.expanduser("~/Library/Caches/Cursor"),
            "/Applications/Cursor.app",
            os.path.expanduser("~/Library/Preferences/com.cursor.app.plist"),
        ]
    elif platform.system() == "Windows":
        paths = [
            os.path.expanduser("~\\AppData\\Local\\Cursor"),
            os.path.expanduser("~\\AppData\\Roaming\\Cursor"),
            os.path.expanduser("~\\.cursor"),
            os.path.expanduser("~\\.config\\Cursor"),
            os.path.expanduser("~\\.cache\\Cursor"),
            "C:\\Program Files\\Cursor",
            "C:\\Program Files (x86)\\Cursor",
            "C:\\Users\\%USERNAME%\\AppData\\Local\\Cursor",
            "C:\\Users\\%USERNAME%\\AppData\\Roaming\\Cursor",
        ]

    # Remove directories
    for path in paths:
        delete_directory(path)

    # Remove common files related to Cursor
    files = [
        os.path.expanduser("~/.cursor/machine-id.db"),
        os.path.expanduser("~/.local/share/cursor.db"),
        os.path.expanduser("~/.config/cursor/preferences.json"),
        os.path.expanduser("~/.cache/cursor.log"),
    ]

    for file in files:
        delete_file(file)

    # Extra cleanup (wildcard search)
    print("\n🔍 Deep scanning for hidden Cursor files...")
    base_dirs = ["/tmp", "/var/tmp", os.path.expanduser("~")]  # Linux and macOS
    if platform.system() == "Windows":
        base_dirs = ["C:\\Temp", "C:\\Windows\\Temp", os.path.expanduser("~")]  # Windows

    for base in base_dirs:
        for root, dirs, files in os.walk(base):
            for dir in dirs:
                if "cursor" in dir.lower():
                    delete_directory(os.path.join(root, dir))
            for file in files:
                if "cursor" in file.lower():
                    delete_file(os.path.join(root, file))

    # Reset machine ID
    reset_machine_id()

    print("\n✅ Cursor AI has been completely reset!")

def main():
    start_time = time.time()
    
    # Display features and warnings
    display_features_and_warnings()
    
    # Get user confirmation
    if get_user_confirmation():
        reset_cursor()
        end_time = time.time()
        print(f"\n⏱️ Completed in {end_time - start_time:.2f} seconds.")
    else:
        print("\n❌ Operation cancelled by user.")

if __name__ == '__main__':
    main()
