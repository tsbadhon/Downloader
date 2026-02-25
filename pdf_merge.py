#!/usr/bin/env python3
"""
PDF Merger Script
Merge multiple PDF files into a single PDF document.
Asks user for sorting preference (by name or date) and folder location.
"""

import os
import sys
import re
from PyPDF2 import PdfMerger, PdfReader
from pathlib import Path

def natural_sort_key(text):
    """
    Convert text to a list of string and integer parts for natural sorting.
    e.g., 'ch10' becomes ['ch', 10] instead of ['c', 'h', '1', '0']
    """
    def convert(text_part):
        return int(text_part) if text_part.isdigit() else text_part.lower()
    
    # Split into alphabetical and numeric parts
    return [convert(c) for c in re.split('([0-9]+)', str(text))]

def get_sort_choice():
    """Ask user whether to sort by name or date."""
    while True:
        print("\nHow would you like to sort the PDF files?")
        print("1. By name (natural order: ch1, ch2, ch10, ch11...)")
        print("2. By date (modification time, oldest first)")
        
        choice = input("Enter your choice (1 or 2): ").strip()
        
        if choice == '1':
            return 'name'
        elif choice == '2':
            return 'date'
        else:
            print("Invalid choice. Please enter 1 or 2.")

def get_folder_path():
    """Ask user for folder path containing PDF files."""
    while True:
        folder = input("\nEnter the folder path containing PDF files: ").strip()
        
        # Remove quotes if user pasted path with quotes
        folder = folder.strip('"').strip("'")
        
        folder_path = Path(folder)
        
        if folder_path.is_dir():
            return folder_path
        else:
            print(f"Error: Folder '{folder}' not found. Please try again.")

def get_pdf_files(folder_path, sort_by):
    """
    Get PDF files from folder and sort them according to user preference.
    Returns list of PDF file paths.
    """
    # Get all PDF files from the folder
    pdf_files = list(folder_path.glob("*.pdf"))
    
    if not pdf_files:
        print(f"\nError: No PDF files found in '{folder_path}'")
        sys.exit(1)
    
    # Sort files according to user preference
    if sort_by == 'name':
        # Use natural sorting for filenames
        pdf_files.sort(key=lambda x: natural_sort_key(x.stem))
        print("\nSorting files by name (natural order: ch1, ch2, ch10, ch11...)...")
    else:  # sort_by == 'date'
        pdf_files.sort(key=lambda x: x.stat().st_mtime)
        print("\nSorting files by date (oldest first)...")
    
    # Display the files that will be merged
    print("\nFiles to be merged (in this order):")
    for i, pdf in enumerate(pdf_files, 1):
        if sort_by == 'date':
            mod_time = os.path.getmtime(pdf)
            from datetime import datetime
            mod_date = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
            print(f"{i:2d}. {pdf.name} (Modified: {mod_date})")
        else:
            print(f"{i:2d}. {pdf.name}")
    
    # Ask for confirmation
    while True:
        confirm = input("\nProceed with merging these files? (y/n): ").strip().lower()
        if confirm in ['y', 'yes']:
            return pdf_files
        elif confirm in ['n', 'no']:
            print("Operation cancelled.")
            sys.exit(0)
        else:
            print("Please enter 'y' or 'n'.")

def get_output_filename(folder_path):
    """Ask user for output filename."""
    default_name = "merged.pdf"
    output = input(f"\nEnter output filename (default: {default_name}): ").strip()
    
    if not output:
        output = default_name
    
    # Ensure .pdf extension
    if not output.lower().endswith('.pdf'):
        output += '.pdf'
    
    # Create full path
    output_path = folder_path / output
    
    # Check if file already exists
    if output_path.exists():
        while True:
            overwrite = input(f"File '{output}' already exists. Overwrite? (y/n): ").strip().lower()
            if overwrite in ['y', 'yes']:
                break
            elif overwrite in ['n', 'no']:
                return get_output_filename(folder_path)
            else:
                print("Please enter 'y' or 'n'.")
    
    return str(output_path)

def merge_pdfs(pdf_files, output_filename):
    """
    Merge multiple PDF files into one.
    """
    if not pdf_files:
        print("Error: No PDF files to merge.")
        sys.exit(1)
    
    merger = PdfMerger()
    
    try:
        print("\nMerging PDF files...")
        for pdf in pdf_files:
            print(f"  Adding: {pdf.name}")
            merger.append(str(pdf))
        
        # Write merged PDF
        merger.write(output_filename)
        merger.close()
        print(f"\n✅ Successfully created: {output_filename}")
        print(f"   Merged {len(pdf_files)} PDF files.")
        
    except Exception as e:
        print(f"\n❌ Error during merge: {e}")
        sys.exit(1)

def main():
    print("=" * 60)
    print("PDF MERGER TOOL")
    print("=" * 60)
    
    # Get sorting preference
    sort_by = get_sort_choice()
    
    # Get folder path
    folder_path = get_folder_path()
    
    # Get PDF files and sort them
    pdf_files = get_pdf_files(folder_path, sort_by)
    
    # Get output filename
    output_filename = get_output_filename(folder_path)
    
    # Merge PDFs
    merge_pdfs(pdf_files, output_filename)
    
    print("\n" + "=" * 60)
    print("Thank you for using PDF Merger Tool!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)