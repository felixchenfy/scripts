#!/bin/bash

# Script: rename_images_based_on_original_timestamp.sh
# Description:
# This script processes image files in a specified folder by performing the following actions:
# 1. It extracts the 'DateTimeOriginal' metadata from the image files and sorts them based on this timestamp.
# 2. Removes all metadata from the images except for the orientation information, which preserves the correct image rotation.
# 3. Renames the image files based on their original 'DateTimeOriginal' timestamps in the format 'MM-DD-HH-MM-SS'.
# 4. Moves the processed images into a subdirectory named "result" within the specified folder.
# 5. Handles potential duplicate filenames by appending a numerical suffix to ensure uniqueness.
# 6. Filters and processes only valid image files (JPEG, PNG, TIFF) and skips directories or unsupported file types.
#
# Usage:
#   ./rename_images_based_on_original_timestamp.sh <folder_path>
#
# Requirements:
#   - exiftool must be installed and accessible in the system's PATH.
#   - The specified folder should contain image files with correct extensions (.jpg, .jpeg, .png, .tiff, .tif).
#
# Example:
#   ./rename_images_based_on_original_timestamp.sh "/path/to/your/folder"
#
# Note:
#   - The script assumes that the input folder contains image files with correct file extensions.
#   - The script creates a "result" subdirectory where the processed images will be moved.
#   - Non-image files or files without 'DateTimeOriginal' metadata are skipped.

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

# Temporary file to hold filenames and their DateTimeOriginal timestamps
temp_file=$(mktemp)

# Find image files and extract DateTimeOriginal and FileName in tab-delimited format
find "$folder_path" -maxdepth 1 -type f \( \
    -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o \
    -iname "*.tif" -o -iname "*.tiff" \
    \) -print0 | xargs -0 exiftool -DateTimeOriginal -FileName -T > "$temp_file"

# Check if temp_file is not empty
if [ ! -s "$temp_file" ]; then
    echo "No image files with 'DateTimeOriginal' metadata found in '$folder_path'."
    rm "$temp_file"
    exit 0
fi

# Sort the temp_file based on the DateTimeOriginal field (first field)
sort -k1,1 "$temp_file" > "${temp_file}_sorted"

# Loop through each line in the sorted file
while IFS=$'\t' read -r datetime_original filename; do
    # Check if variables are not empty
    if [ -z "$datetime_original" ] || [ -z "$filename" ]; then
        echo "Skipping file due to missing DateTimeOriginal or filename."
        continue
    fi

    # Full path to the file
    filepath="$folder_path/$filename"

    # Ensure the file actually exists
    if [ ! -f "$filepath" ]; then
        echo "Skipping invalid or unsupported file: '$filename'"
        continue
    fi

    # Check MIME type to ensure it's an image
    mime_type=$(file --mime-type -b "$filepath")
    if [[ "$mime_type" != image/* ]]; then
        echo "Skipping invalid or unsupported file: '$filename' (MIME type: $mime_type)"
        continue
    fi

    # Format 'DateTimeOriginal' to 'MM-DD-HH-MM-SS'
    # Replace first two ':' with '-' to make it 'YYYY-MM-DD HH:MM:SS'
    formatted_datetime=$(echo "$datetime_original" | sed 's/:/-/;s/:/-/')

    # Convert to timestamp to ensure valid date
    timestamp=$(date -d "$formatted_datetime" +%s 2>/dev/null)
    if [ -z "$timestamp" ]; then
        echo "Skipping file due to invalid DateTimeOriginal: '$filename'"
        continue
    fi

    # Generate new filename based on original timestamp
    new_filename_date=$(date -d "$formatted_datetime" '+%m-%d-%H-%M-%S')

    # Remove all metadata except for Orientation
    exiftool -overwrite_original \
        -All= \
        -TagsFromFile @ -Orientation \
        -UserComment= \
        -DocumentID= \
        -InstanceID= \
        -OriginalDocumentID= \
        "$filepath" > /dev/null

    # Extract file extension
    extension="${filename##*.}"
    extension="${extension,,}" # Convert to lowercase

    # Check for duplicates and add suffix if needed
    new_filename="${new_filename_date}.${extension}"
    suffix=1
    while [ -e "$result_folder/$new_filename" ]; do
        new_filename="${new_filename_date}_$(printf "%02d" $suffix).${extension}"
        suffix=$((suffix + 1))
    done

    # Move the file to the result folder with the new name
    mv "$filepath" "$result_folder/$new_filename"

done < "${temp_file}_sorted"

# Clean up temporary files
rm "$temp_file" "${temp_file}_sorted"

echo "Processed images by removing metadata (except orientation) and renamed files based on original timestamps."
