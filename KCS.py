import os
import subprocess
import zipfile
import shutil
import re
from pathlib import Path
import sys

# Configuration
APK_EDITOR_JAR = "/storage/emulated/0/YouTube/Cookies/APKEditor-1.4.3.jar"
KEYSTORE_PATH = "Sajanagarwal.keystore"  # Will be created in the same directory as the APKS
KEYSTORE_PASS = "Sajanagarwal"
KEY_ALIAS = "Sajanagarwal"
KEY_PASS = "Sajanagarwal"
APKSIGNER_PATH = "apksigner"
VALIDITY_DAYS = 36500  # ~100 years

def get_file_path():
    """Ask user for APK/APKS/XAPK/APKM file path and return it"""
    while True:
        file_path = input("Enter the full path to your APK/APKS/XAPK/APKM file: ").strip()
        if not os.path.exists(file_path):
            print(f"Error: File not found at {file_path}")
            continue
        return file_path

def find_newest_matching_file(directory, pattern):
    """Find the newest file in directory matching the pattern"""
    files = []
    for f in os.listdir(directory):
        if re.search(pattern, f):
            files.append(os.path.join(directory, f))
    
    if not files:
        return None
    
    return max(files, key=os.path.getmtime)

def delete_file_if_exists(file_path):
    """Delete a file if it exists"""
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"Deleted: {os.path.basename(file_path)}")
            return True
        except Exception as e:
            print(f"Error deleting {os.path.basename(file_path)}: {str(e)}")
            return False
    return True

def convert_apks_to_apk(apks_path):
    if not os.path.exists(apks_path):
        print(f"Error: File not found at {apks_path}")
        return None
    
    base_name = os.path.splitext(os.path.basename(apks_path))[0]
    output_filename = f"{base_name}.apk"
    output_path = os.path.join(os.path.dirname(apks_path), output_filename)
    
    command = f"java -jar {APK_EDITOR_JAR} m -i \"{apks_path}\" -o \"{output_path}\""
    
    try:
        print(f"Converting {os.path.basename(apks_path)} to APK...")
        result = subprocess.run(command, shell=True, check=True, text=True)
        print(f"Success! APK created as {output_filename}")
        
        # Delete the original APKS file after successful conversion
        delete_file_if_exists(apks_path)
        
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def kill_signature_verification(apk_path):
    if not shutil.which("sigtool"):
        print("Error: sigtool not found. Please install MT Manager first.")
        return None
    
    apk_dir = os.path.dirname(apk_path)
    apk_name = os.path.basename(apk_path)
    
    print("\nGenerating MT hook...")
    hook_command = f"sigtool \"{apk_path}\" -hmt"
    subprocess.run(hook_command, shell=True)
    
    hook_zip = find_newest_matching_file(apk_dir, r"mthook_.*\.zip")
    
    if not hook_zip or not os.path.exists(hook_zip):
        print("Error: Failed to find generated hook zip file.")
        print("Tried to find pattern: mthook_*.zip")
        print("Files in directory:")
        for f in os.listdir(apk_dir):
            print(f" - {f}")
        return None
    
    print(f"\nHook generated: {hook_zip}")
    
    temp_dir = os.path.join(apk_dir, "temp_hook")
    os.makedirs(temp_dir, exist_ok=True)
    
    print("\nExtracting hook contents...")
    with zipfile.ZipFile(hook_zip, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    
    # Create backup file first
    bak_path = os.path.join(apk_dir, f"{os.path.splitext(apk_name)[0]}.bak")
    shutil.copy(apk_path, bak_path)
    
    modified_apk = os.path.join(apk_dir, f"modified_{apk_name}")
    
    print("\nAdding hook to original APK...")
    with zipfile.ZipFile(apk_path, 'a') as apk_zip:
        for root, _, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                print(f"Adding: {arcname}")
                apk_zip.write(file_path, arcname)
    
    shutil.rmtree(temp_dir)
    
    # Delete the backup file after successful modification
    delete_file_if_exists(bak_path)
    
    print("\nSignature verification killed successfully!")
    return apk_path  # Return the modified original path since we modified it in place

def find_keytool():
    possible_paths = [
        "/data/data/com.termux/files/usr/bin/keytool",
        "/data/data/com.termux/files/usr/opt/openjdk/bin/keytool",
        "/data/data/com.termux/files/usr/lib/jvm/openjdk-9/bin/keytool",
        "keytool"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

def get_certificate_info():
    print("\nEnter certificate information (press Enter to skip any field):")
    
    cert_info = {
        'CN': '',
        'OU': '',
        'O': '',
        'L': '',
        'ST': '',
        'C': ''
    }
    
    cert_info['CN'] = input("Common Name (CN): ").strip()
    cert_info['OU'] = input("Organizational Unit (OU): ").strip()
    cert_info['O'] = input("Organization (O): ").strip()
    cert_info['L'] = input("Locality (L): ").strip()
    cert_info['ST'] = input("State (ST): ").strip()
    cert_info['C'] = input("Country Code (C, 2 letters): ").strip().upper()
    
    return {k: v for k, v in cert_info.items() if v}

def generate_keystore(working_dir, cert_info):
    print("\nGenerating new keystore...")
    
    keytool_path = find_keytool()
    if not keytool_path:
        print("\nError: keytool not found. Please ensure OpenJDK is installed in Termux.")
        print("Install it with: pkg install openjdk-17")
        return False
    
    dname_parts = []
    if 'CN' in cert_info:
        dname_parts.append(f"CN={cert_info['CN']}")
    if 'OU' in cert_info:
        dname_parts.append(f"OU={cert_info['OU']}")
    if 'O' in cert_info:
        dname_parts.append(f"O={cert_info['O']}")
    if 'L' in cert_info:
        dname_parts.append(f"L={cert_info['L']}")
    if 'ST' in cert_info:
        dname_parts.append(f"ST={cert_info['ST']}")
    if 'C' in cert_info:
        dname_parts.append(f"C={cert_info['C']}")
    
    dname = ", ".join(dname_parts)
    keystore_path = os.path.join(working_dir, KEYSTORE_PATH)
    
    cmd = [
        keytool_path,
        "-genkey",
        "-v",
        "-keystore", keystore_path,
        "-alias", KEY_ALIAS,
        "-keyalg", "RSA",
        "-keysize", "2048",
        "-validity", str(VALIDITY_DAYS),
        "-dname", dname,
        "-storepass", KEYSTORE_PASS,
        "-keypass", KEY_PASS
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"\nKeystore created at {keystore_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nError creating keystore: {e}")
        return False

def sign_apk(apk_path):
    working_dir = os.path.dirname(apk_path)
    base_name = os.path.splitext(os.path.basename(apk_path))[0]
    if base_name.startswith('modified_'):
        base_name = base_name[9:]  # Remove 'modified_' prefix
    
    signed_apk_path = os.path.join(working_dir, f"signed_{base_name}.apk")
    keystore_path = os.path.join(working_dir, KEYSTORE_PATH)
    
    if not os.path.exists(apk_path):
        print(f"\nError: APK file not found at {apk_path}")
        return None
    
    print(f"\nSigning {os.path.basename(apk_path)}...")
    
    cmd = [
        APKSIGNER_PATH, "sign",
        "--ks", keystore_path,
        "--ks-pass", f"pass:{KEYSTORE_PASS}",
        "--ks-key-alias", KEY_ALIAS,
        "--key-pass", f"pass:{KEY_PASS}",
        "--out", signed_apk_path,
        "--v1-signing-enabled", "false",
        "--v2-signing-enabled", "true",
        "--v3-signing-enabled", "true",
        apk_path
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"\nSuccess! Signed APK saved as: {os.path.basename(signed_apk_path)}")
        
        # Delete the unsigned APK after successful signing
        delete_file_if_exists(apk_path)
        
        return signed_apk_path
    except subprocess.CalledProcessError as e:
        print(f"\nError signing APK: {e}")
        return None

def clean_directory(working_dir, keep_last_modified=True):
    """Clean up temporary files, keeping only the final signed APK and essential files"""
    keep_files = {
        os.path.basename(APK_EDITOR_JAR),
        KEYSTORE_PATH
    }
    
    try:
        if not os.path.exists(working_dir):
            print(f"Error: Directory {working_dir} does not exist")
            return False
        
        files = os.listdir(working_dir)
        deleted_count = 0
        error_count = 0
        
        # Find the newest signed APK to keep
        signed_apks = [f for f in files if f.startswith("signed_") and f.endswith(".apk")]
        if signed_apks:
            newest_signed = max(signed_apks, key=lambda f: os.path.getmtime(os.path.join(working_dir, f)))
            keep_files.add(newest_signed)
        
        # If we should keep the last modified APK (when not signing)
        if keep_last_modified:
            modified_apks = [f for f in files if f.startswith("modified_") and f.endswith(".apk")]
            if modified_apks:
                newest_modified = max(modified_apks, key=lambda f: os.path.getmtime(os.path.join(working_dir, f)))
                keep_files.add(newest_modified)
            else:
                # If no modified APK, keep the newest regular APK
                regular_apks = [f for f in files if f.endswith(".apk") and not f.startswith(("modified_", "signed_"))]
                if regular_apks:
                    newest_regular = max(regular_apks, key=lambda f: os.path.getmtime(os.path.join(working_dir, f)))
                    keep_files.add(newest_regular)
        
        for file in files:
            file_path = os.path.join(working_dir, file)
            
            if file in keep_files or os.path.isdir(file_path):
                continue
            
            try:
                os.remove(file_path)
                print(f"Deleted: {file}")
                deleted_count += 1
            except Exception as e:
                print(f"Error deleting {file}: {str(e)}")
                error_count += 1
        
        print(f"\nCleanup complete. Deleted {deleted_count} files with {error_count} errors.")
        return True
    
    except Exception as e:
        print(f"An unexpected error occurred during cleanup: {str(e)}")
        return False

def main():
    print("\nAPK Conversion and Signing Tool")
    print("=" * 40)
    
    # Get file path from user
    input_path = get_file_path()
    working_dir = os.path.dirname(input_path)
    file_ext = os.path.splitext(input_path)[1].lower()
    
    if file_ext == '.apk':
        # Only kill signature verification for APK files
        kill_sig = input("\nDo you want to kill signature verification? (y/n): ").strip().lower()
        if kill_sig == 'y':
            modified_apk = kill_signature_verification(input_path)
            if modified_apk:
                print("\nProcess completed! Only signature verification was killed for the APK file.")
                return
        else:
            print("\nNo changes made to the APK file.")
            return
    else:
        # For APKS/XAPK/APKM files, perform the original workflow
        apk_path = convert_apks_to_apk(input_path)
        if not apk_path:
            return
        
        kill_sig = input("\nDo you want to kill signature verification? (y/n): ").strip().lower()
        if kill_sig == 'y':
            modified_apk = kill_signature_verification(apk_path)
            if modified_apk:
                apk_path = modified_apk
        
        sign = input("\nDo you want to sign the APK? (y/n): ").strip().lower()
        if sign == 'y':
            keystore_path = os.path.join(working_dir, KEYSTORE_PATH)
            if not os.path.exists(keystore_path):
                print("\nNo existing keystore found. Please provide certificate information for new keystore.")
                cert_info = get_certificate_info()
                if not generate_keystore(working_dir, cert_info):
                    return
            else:
                print("\nUsing existing keystore")
                use_existing = input("Do you want to use the existing keystore? (y/n): ").strip().lower()
                if use_existing == 'n':
                    cert_info = get_certificate_info()
                    if not generate_keystore(working_dir, cert_info):
                        return
            
            signed_apk = sign_apk(apk_path)
            if signed_apk:
                print(f"\nFinal signed APK: {signed_apk}")
            else:
                print("\nFailed to sign APK")
            
            # When signing, we don't need to keep the modified/unsigned APK
            print("\nStarting cleanup...")
            success = clean_directory(working_dir, keep_last_modified=False)
        else:
            print("\nSkipping signing process")
            # When not signing, we want to keep the last modified/unsigned APK
            print("\nStarting cleanup (keeping last modified APK)...")
            success = clean_directory(working_dir, keep_last_modified=True)
        
        if not success:
            sys.exit(1)
    
    print("\nProcess completed!")

if __name__ == "__main__":
    main()