#!/bin/bash
# Rename all files in the given folder with a random string of 8 characters of a-z and A-Z, preserving the original file suffix.

# Check if folder path is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <folder_path>"
    exit 1
fi

# Change to the specified directory
cd "$1"

# Function to generate a random string of 8 characters (alphanumeric)
generate_random_string() {
    cat /dev/urandom | tr -dc 'a-zA-Z' | fold -w 8 | head -n 1
}


# Regex pattern to match specific file naming
pattern="^[0-9]+-[0-9]+-[a-zA-Z0-9]{8}\.[a-zA-Z]+$"

# Process all files in the directory
for file in *; do
    if [ -f "$file" ]; then
        # Extract file extension
        extension="${file##*.}"
        echo "Rename file: $file"
        if [[ $file =~ $pattern ]]; then
            # File matches the specific pattern, generate special string
            new_string=$(generate_random_string)
            new_name="$(echo $file | sed -r "s/([0-9]+-[0-9]+-)[a-zA-Z0-9]{8}(\.[a-zA-Z]+)/\1$new_string\2/")"
        else
            # File does not match the pattern, generate random string
            random_string=$(generate_random_string)
            new_name="${random_string}.${extension}"
        fi

        # Rename the file
        mv "$file" "$new_name"
    fi
done

echo "File processing complete."
