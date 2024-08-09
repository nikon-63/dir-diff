#!/usr/bin/env python3
# Imports 
import os
import sys
import filecmp
import argparse
import hashlib
from datetime import datetime

# Colors for the output to make it more readable
COLOR_RESET = "\033[0m" # Set to default color
COLOR_RED = "\033[31m" # Set to red
COLOR_GREEN = "\033[32m" # Set to green
COLOR_YELLOW = "\033[33m" # Set to yellow
COLOR_CYAN = "\033[36m"     # Set to cyan
COLOR_MAGENTA = "\033[35m" # Set to magenta
COLOR_WHITE = "\033[37m" # Set to white
COLOR_BLUE = "\033[34m" # Set to blue
COLOR_BOLD = "\033[1m" # Set to bold

def print_directory_details(dir1, dir2):
    print(f"{COLOR_BOLD}{COLOR_CYAN}=== Directory Details: {dir1} ==={COLOR_RESET}")
    print_directory_info(dir1)
    print(f"{COLOR_BOLD}{COLOR_CYAN}=== Directory Details: {dir2} ==={COLOR_RESET}")
    print_directory_info(dir2)

def print_directory_info(directory):
    dir_hash = compute_directory_hash(directory) # Calls function to work out the hash of the directory
    last_modified = datetime.fromtimestamp(os.path.getmtime(directory)).strftime('%Y-%m-%d %H:%M:%S')
    created = datetime.fromtimestamp(os.path.getctime(directory)).strftime('%Y-%m-%d %H:%M:%S')
    print(f"{COLOR_BOLD}{COLOR_GREEN}-- Directory: {os.path.basename(directory)}{COLOR_RESET}")
    print(f"    {COLOR_WHITE}Path: {directory}{COLOR_RESET}")
    print(f"    {COLOR_WHITE}Hash: {dir_hash}{COLOR_RESET}")
    print(f"    {COLOR_WHITE}Last Modified: {last_modified}{COLOR_RESET}")
    print(f"    {COLOR_WHITE}Created: {created}{COLOR_RESET}")
    print()

def compute_directory_hash(directory): # Working out the hash of the directory
    hasher = hashlib.sha256() # SHA-256
    for root, dirs, files in os.walk(directory):
        for names in files + dirs:
            filepath = os.path.join(root, names)
            hasher.update(filepath.encode())
            if os.path.isfile(filepath):
                with open(filepath, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hasher.update(chunk)
        break  # Only consider the root directory itself
    return hasher.hexdigest()

def compare_directories(dir1, dir2, verbose): # Added V to make it more readable

    comparison = filecmp.dircmp(dir1, dir2)

    print(f"{COLOR_BOLD}{COLOR_CYAN}=== Differences between directories ==={COLOR_RESET}")
    
    # Work out the differences between the directories
    # Files only in dir1
    if comparison.left_only:
        print(f"{COLOR_BOLD}{COLOR_YELLOW}Files only in {dir1}{COLOR_RESET}")
        for file in comparison.left_only:
            print(f"  {COLOR_BOLD}{COLOR_GREEN}-- {file}{COLOR_RESET}")
    
    # Files only in dir2
    if comparison.right_only:
        print(f"{COLOR_BOLD}{COLOR_YELLOW}Files only in {dir2}{COLOR_RESET}")
        for file in comparison.right_only:
            print(f"  {COLOR_BOLD}{COLOR_GREEN}-- {file}{COLOR_RESET}")
    
    # Files that are in both difrrent
    if comparison.diff_files:
        print(f"{COLOR_BOLD}{COLOR_YELLOW}Files that differ between {dir1} and {dir2}{COLOR_RESET}")
        for file in comparison.diff_files:
            file1_path = os.path.join(dir1, file)
            file2_path = os.path.join(dir2, file)
            print(f"  {COLOR_BOLD}{COLOR_GREEN}-- {file}{COLOR_RESET}")
            if is_text_file(file1_path) and is_text_file(file2_path):
                compare_files_line_by_line(file1_path, file2_path, verbose) # Only dose it if they are text files
            else:
                compare_binary_files(file1_path, file2_path) # If they are not human readable then jsut compare the hash

    # Where the same files are
    if comparison.same_files:
        print(f"{COLOR_BOLD}{COLOR_CYAN}=== Files that are identical in both directories ==={COLOR_RESET}")
        for file in comparison.same_files:
            print(f"  {COLOR_BOLD}{COLOR_GREEN}-- {file}{COLOR_RESET}")

    # To look though all the subdirectories
    for subdir in comparison.common_dirs:
        print(f"\n{COLOR_BOLD}{COLOR_CYAN}Comparing subdirectory: {subdir}{COLOR_RESET}")
        compare_directories(os.path.join(dir1, subdir), os.path.join(dir2, subdir), verbose)

def is_text_file(file_path): # Had to add this as images used to brake the code
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            file.read()
        return True
    except UnicodeDecodeError:
        return False

def compare_files_line_by_line(file1, file2, verbose): 
    with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
        file1_lines = f1.readlines()
        file2_lines = f2.readlines()

    min_len = min(len(file1_lines), len(file2_lines))
    diff_count = 0  #Used to know when to stop printing differences if there are more than 3

    for i in range(min_len):
        if file1_lines[i] != file2_lines[i]:
            if not verbose and diff_count >= 3: # Only show 3 differences if not V
                print(f"    {COLOR_BOLD}{COLOR_YELLOW}...{COLOR_RESET} (more differences not shown)")
                break
            print(f"    {COLOR_BOLD}{COLOR_RED}Difference at line {i+1}:{COLOR_RESET}")
            print(f"      {COLOR_BOLD}{COLOR_YELLOW}{file1}:{COLOR_WHITE} {file1_lines[i].strip()}{COLOR_RESET}")
            print(f"      {COLOR_BOLD}{COLOR_YELLOW}{file2}:{COLOR_WHITE} {file2_lines[i].strip()}{COLOR_RESET}")
            diff_count += 1

# TODO Need to make into one function 
    if len(file1_lines) > min_len and (verbose or diff_count < 3): # Prints if there are additional lines in one of the files
        print(f"    {COLOR_BOLD}{COLOR_YELLOW}Additional lines in {file1} starting at line {min_len + 1}:{COLOR_RESET}")
        for line in file1_lines[min_len:]:
            if not verbose and diff_count >= 3: # Same use to know when to stop printing if V not set 
                print(f"    {COLOR_BOLD}{COLOR_YELLOW}...{COLOR_RESET} (more differences not shown)")
                break
            print(f"      {COLOR_WHITE}{line.strip()}{COLOR_RESET}")
            diff_count += 1

    if len(file2_lines) > min_len and (verbose or diff_count < 3): # Same as other just for the other file 
        print(f"    {COLOR_BOLD}{COLOR_YELLOW}Additional lines in {file2} starting at line {min_len + 1}:{COLOR_RESET}")
        for line in file2_lines[min_len:]:
            if not verbose and diff_count >= 3:
                print(f"    {COLOR_BOLD}{COLOR_YELLOW}...{COLOR_RESET} (more differences not shown)")
                break
            print(f"      {COLOR_WHITE}{line.strip()}{COLOR_RESET}")
            diff_count += 1

def compare_binary_files(file1, file2): # If not a test file
    hash1 = compute_file_hash(file1)
    hash2 = compute_file_hash(file2)

    if hash1 != hash2:
        print(f"    {COLOR_BOLD}{COLOR_MAGENTA}Binary files differ:{COLOR_RESET}")
        print(f"      {COLOR_BOLD}{file1}{COLOR_RESET}")
        print(f"      {COLOR_BOLD}{file2}{COLOR_RESET}")

def compute_file_hash(file_path): # Working out file has with SHA-256
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def main(): # Main function
    # How to use the tool
    parser = argparse.ArgumentParser(description="Compare two directories and show differences.") 
    parser.add_argument("dir1", help="First directory to compare")
    parser.add_argument("dir2", help="Second directory to compare")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print all differences")
    args = parser.parse_args()

    # Brakes if if not directories
    if not os.path.isdir(args.dir1) or not os.path.isdir(args.dir2):
        print(f"{COLOR_BOLD}{COLOR_RED}Both arguments must be directories{COLOR_RESET}")
        sys.exit(1)
    
    # Starts function
    print_directory_details(args.dir1, args.dir2) # Print directory details
    compare_directories(args.dir1, args.dir2, args.verbose) # Compare directories

if __name__ == "__main__":
    main()
