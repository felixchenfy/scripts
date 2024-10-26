#!/bin/bash

# Script: set_dummy_date_for_sorted_image_files.sh
# Description:
# This script processes image files in a specified folder by performing the following actions:
# 1. Sorts the images based on their filenames.
# 2. Copies the images to a "result" subdirectory without modifying the original images.
# 3. Sets the creation and modification dates of the images in the "result" folder.
#    - For the first image, sets the date to the current time.
#    - For subsequent images, increments the timestamp by 1 second for each image.

# Usage:
#   ./set_dummy_date_for_sorted_image_files.sh <folder_path>

# Requirements:
#   - The specified folder should contain image files with correct extensions.
#   - The script uses 'exiftool' to modify metadata. Ensure 'exiftool' is installed.

# Example:
#   ./set_dummy_date_for_sorted_image_files.sh "/path/to/your/folder"

# Check if a folder path is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <folder_path>"
    exit 1
fi

# Assign the folder path to a variable
folder_path="$1"

# Check if the provided path is a directory
if [ ! -d "$folder_path" ]; then
    echo "Error: '$folder_path' is not a directory"
    exit 1
fi

# Create a "result" subdirectory within the specified folder
result_folder="$folder_path/result"
mkdir -p "$result_folder"

# Get the current timestamp in seconds since epoch
current_time=$(date +%s)

# Initialize counter for adding seconds
counter=0

# Find image files and sort them by filename
find "$folder_path" -maxdepth 1 -type f \( \
    -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o \
    -iname "*.tif" -o -iname "*.tiff" -o -iname "*.gif" \
    -o -iname "*.bmp" -o -iname "*.heic" \
    \) -print0 | sort -z | while IFS= read -r -d '' filepath; do

    # Get the filename from the path
    filename=$(basename "$filepath")

    # Copy the file to the result folder
    cp "$filepath" "$result_folder/$filename"

    # Calculate the timestamp for this file
    timestamp=$((current_time + counter))

    # Convert the timestamp to the proper format
    date_string=$(date -d "@$timestamp" '+%Y:%m:%d %H:%M:%S')

    # Modify the creation and modification dates
    exiftool -overwrite_original \
        -FileModifyDate="$date_string" \
        -FileCreateDate="$date_string" \
        -ModifyDate="$date_string" \
        -DateTimeOriginal="$date_string" \
        "$result_folder/$filename" > /dev/null

    # Increment the counter by 1 second
    counter=$((counter + 1))
done

echo "Processed images with updated timestamps in '$result_folder'."
