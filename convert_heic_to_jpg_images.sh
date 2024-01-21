#!/bin/bash

# Check if a directory is given
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

DIR=$1

# Check if the given directory exists
if [ ! -d "$DIR" ]; then
    echo "Directory not found: $DIR"
    exit 1
fi

# Convert all HEIC files to JPG
for file in "$DIR"/*.HEIC; do
    if [ -f "$file" ]; then
        echo "Converting $file ..."
        heif-convert "$file" "${file%.HEIC}.jpg"
    fi
done

echo "Conversion complete."
