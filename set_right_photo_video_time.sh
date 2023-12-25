#!/bin/bash

# This script adjusts the creation and modification times of photos and videos to match their metadata.
# It's designed to correct timestamps for items downloaded from iCloud Photos.
# Note: This only works for camera photos, camera videos, and screenshots.
# Images from other sources, like web downloads, are not supported.
# 
# Prerequisites:
# 1. Install exiftool:
#    Ubuntu: sudo apt-get install exiftool
# 2. Install ImageMagick (for handling HEIC files):
#    Ubuntu: sudo apt-get install imagemagick
#
# Usage:
# ./this_script.sh /path/to/media/directory

# Directory containing the media (passed as the first argument)
MEDIA_DIR="$1"

# Check if MEDIA_DIR is provided
if [ -z "$MEDIA_DIR" ]; then
    echo "Please provide a directory."
    exit 1
fi

# Function to extract datetime and update file timestamp
update_timestamp() {
    local file=$1
    local is_video=$2
    local datetime_tag="DateTimeOriginal"

    # If the file is a video, use the 'CreateDate' tag instead
    if [ "$is_video" == true ]; then
        datetime_tag="CreateDate"
    fi

    datetime=$(exiftool -$datetime_tag -d "%Y%m%d%H%M.%S" "$file" | awk -F': ' '{print $2}')
    
    if [ ! -z "$datetime" ]; then
        touch -t "$datetime" "$file"
        if [ "$is_video" == true ]; then
            echo "Successfully updated timestamp for video $file"
        else
            echo "Successfully updated timestamp for image $file"
        fi
    else
        if [ "$is_video" == false ]; then
            echo "No EXIF data for image $file"
        else
            echo "No metadata for video $file"
        fi
    fi
}

# Loop over each file in the directory
for file in "$MEDIA_DIR"/*; do
    if [[ -f "$file" ]]; then
        # Check if the file is a common video format
        if [[ "$file" == *.mp4 || "$file" == *.MP4 || "$file" == *.mov || "$file" == *.MOV || "$file" == *.avi || "$file" == *.AVI ]]; then
            # Handle video file
            update_timestamp "$file" true
        else
            # Handle image file
            update_timestamp "$file" false
        fi
    fi
done
