import os
import shutil
import platform
import time

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
            os.path.expanduser("~/.local/share/cursor"),
            os.path.expanduser("~/.config/Cursor"),
            os.path.expanduser("~/.local/share/Cursor"),
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
    
    print("\n✅ Cursor AI has been completely reset!")

def main():
    start_time = time.time()
    reset_cursor()
    end_time = time.time()
    print(f"\n⏱️ Completed in {end_time - start_time:.2f} seconds.")

if __name__ == '__main__':
    main()
