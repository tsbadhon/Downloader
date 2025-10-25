import os
import subprocess

def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {command}\nError: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def setup_termux_storage():
    print("\n📁 Setting up Termux storage permissions...")
    if not run_command("termux-setup-storage"):
        print("⚠️ Could not setup storage automatically. Please run 'termux-setup-storage' manually.")
    
    # Create required YouTube directories
    print("\n📂 Creating YouTube directories...")
    directories = [
        "/storage/emulated/0/YouTube/Video",
        "/storage/emulated/0/YouTube/Music",
        "/storage/emulated/0/YouTube/INFO",
        "/storage/emulated/0/YouTube/Tiktok",
        "/storage/emulated/0/SIGN/",
        "/storage/emulated/0/YouTube/Cookies"
    ]
    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                print(f"✅ Created directory: {directory}")
            except Exception as e:
                print(f"❌ Failed to create {directory}: {e}")
        else:
            print(f"ℹ️ Directory already exists: {directory}")

def install_termux_packages():
    # Termux system packages##pkg
    termux_packages = [
        "ffmpeg",
        "libjpeg-turbo",
        "zlib",
        "opus-tools",
        "libffi",
        "pango",
        "libxml2",
        "libxslt",
        "openjpeg",
        "openjdk-17",
        "aapt",
        "rust",
        "apksigner",
        "radare2",
        "wget",
        "zip",
    ]

    print("🔄 Updating Termux packages...")
    run_command("pkg update -y && pkg upgrade -y")

    print("📦 Installing Termux system packages...")
    for pkg in termux_packages:
        if not run_command(f"pkg install -y {pkg}"):
            print(f"⚠️ Could not install {pkg}. You may need to install it manually.")

def install_python_packages():
    # Python packages#pip
    python_packages = [
        "weasyprint",
        "tgcrypto",
        "yt-dlp",
        "pillow",
        "pyrogram",
        "reportlab",
        "tqdm",
        "sigtool",
        "requests",
        "setuptools",
        "google-api-python-client",
    ]

    print("🐍 Installing Python packages...")
    for pkg in python_packages:
        if not run_command(f"pip install --upgrade {pkg}"):
            print(f"⚠️ Could not install {pkg}. Try 'pip3 install {pkg}' manually.")

def main():
    print("🔧 Starting Termux installation...")
    
    # Setup storage access and create directories
    setup_termux_storage()
    
    # Install Termux packages
    install_termux_packages()
    
    # Install Python packages
    install_python_packages()
    
    print("\n✅ Installation completed!")
    print("Important notes:")
    print("- If storage setup failed, run 'termux-setup-storage' manually")
    print("- Grant storage permissions when prompted")
    print("- Some packages may need additional configuration")

if __name__ == "__main__":
    main()