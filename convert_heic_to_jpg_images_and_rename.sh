#!/bin/bash

# HEIC to JPG Conversion Script
# 
# This script converts all .HEIC (case insensitive) files in a given directory to .jpg format.
# The converted files are renamed using the format: <prefix>_00001.jpg, <prefix>_00002.jpg, etc.
# After successful conversion.
# WARNING: the original .HEIC files are deleted.
#
# Usage:
#   ./heic_to_jpg.sh <directory> <prefix>
#
# Example:
#   ./heic_to_jpg.sh /path/to/images vacation
#   This converts and renames images like vacation_00001.jpg, vacation_00002.jpg, etc.
#
# Requirements:
#   heif-convert utility (install with 'sudo apt install libheif-examples' on Ubuntu 
#   or 'brew install libheif' on macOS).

# Check if correct number of arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <directory> <prefix>"
    exit 1
fi

DIR=$1
PREFIX=$2

# Check if the given directory exists
if [ ! -d "$DIR" ]; then
    echo "Directory not found: $DIR"
    exit 1
fi

# Enable case-insensitive globbing for file extensions
shopt -s nullglob nocaseglob

# Find and sort the HEIC files by name
files=("$DIR"/*.heic "$DIR"/*.HEIC)
sorted_files=($(printf "%s\n" "${files[@]}" | sort))

# Initialize the counter
counter=1

# Convert and rename all HEIC files
for file in "${sorted_files[@]}"; do
    if [ -f "$file" ]; then
        echo "Converting $file ..."
        new_filename=$(printf "%s/%s_%05d.jpg" "$DIR" "$PREFIX" "$counter")
        
        # Convert HEIC to JPG and rename
        if heif-convert "$file" "$new_filename"; then
            echo "Successfully converted and renamed to $new_filename"
            
            # Delete the original file after successful conversion
            rm "$file"
            echo "Deleted original file: $file"
        else
            echo "Failed to convert $file"
        fi
        
        # Increment the counter
        ((counter++))
    fi
done

echo "Conversion, renaming, and cleanup complete."
