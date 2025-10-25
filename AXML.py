import os
import subprocess

# Define JAR path
JAR_PATH = "/storage/emulated/0/YouTube/Cookies/axml2xml.jar"

def get_file_path():
    """Ask user for AndroidManifest.xml path and set all paths accordingly."""
    while True:
        input_path = input("Enter the full path to AndroidManifest.xml: ").strip()
        if not os.path.exists(input_path):
            print(f"Error: File not found at {input_path}")
            continue
        
        base_dir = os.path.dirname(input_path)
        file_name = os.path.basename(input_path)
        
        # Set all paths based on user input
        global INPUT_AXML, OUTPUT_XML, RECOMPILED_AXML, FINAL_AXML
        INPUT_AXML = input_path
        OUTPUT_XML = os.path.join(base_dir, f"{os.path.splitext(file_name)[0]}_decoded.xml")
        RECOMPILED_AXML = os.path.join(base_dir, f"{os.path.splitext(file_name)[0]}_recompiled.xml")
        FINAL_AXML = input_path  # Original path will be overwritten
        
        return True

def check_jar():
    """Check if axml2xml.jar exists."""
    if not os.path.exists(JAR_PATH):
        print(f"Error: {JAR_PATH} not found!")
        return False
    return True

def decompile_axml():
    """Decompile AndroidManifest.xml to XML using axml2xml.jar and delete original."""
    try:
        print(f"Decompiling {INPUT_AXML} to {OUTPUT_XML}...")
        result = subprocess.run(
            ["java", "-jar", JAR_PATH, "d", INPUT_AXML, OUTPUT_XML],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"Successfully decompiled to {OUTPUT_XML}")
            # Delete the original AndroidManifest.xml
            try:
                os.remove(INPUT_AXML)
                print(f"Deleted original {INPUT_AXML}")
            except OSError as e:
                print(f"Error deleting {INPUT_AXML}: {e}")
            return True
        else:
            print(f"Error decompiling: {result.stderr}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Error running decompile command: {e}")
        return False

def recompile_xml():
    """Recompile XML to AXML and rename to original AndroidManifest.xml path."""
    try:
        print(f"Recompiling {OUTPUT_XML} to {RECOMPILED_AXML}...")
        result = subprocess.run(
            ["java", "-jar", JAR_PATH, "e", OUTPUT_XML, RECOMPILED_AXML],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"Successfully recompiled to {RECOMPILED_AXML}")
            # Rename recompiled file to original path
            try:
                os.rename(RECOMPILED_AXML, FINAL_AXML)
                print(f"Renamed {RECOMPILED_AXML} to {FINAL_AXML}")
                return True
            except OSError as e:
                print(f"Error renaming {RECOMPILED_AXML} to {FINAL_AXML}: {e}")
                return False
        else:
            print(f"Error recompiling: {result.stderr}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Error running recompile command: {e}")
        return False

def main():
    # Check if JAR exists
    if not check_jar():
        return

    # Get AndroidManifest.xml path from user
    if not get_file_path():
        return

    # Decompile AndroidManifest.xml to XML and delete original
    if decompile_axml():
        print(f"\nDecompilation complete. Output saved to {OUTPUT_XML}")
    else:
        print("Decompilation failed. Exiting...")
        return

    # Prompt for recompilation
    while True:
        choice = input("\nDo you want to recompile the XML back to AXML? (y/n): ").strip().lower()
        if choice == 'y':
            if os.path.exists(OUTPUT_XML):
                if recompile_xml():
                    print("Recompilation and renaming complete.")
                else:
                    print("Recompilation failed.")
            else:
                print(f"Error: {OUTPUT_XML} not found for recompilation!")
            break
        elif choice == 'n':
            print("Exiting without recompiling.")
            break
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

if __name__ == "__main__":
    main()