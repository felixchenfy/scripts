#!/bin/bash

# 1. Read the folder name from the command line argument.
# 2. Iterate through the files in the folder in alphabetical order.
# 3. Parse the file names to extract the year and month (if applicable).
# 4. Modify the file's creation and modification dates based on the extracted date, adding i seconds where i is the file's position in the alphabetical order.
#!/bin/bash

# Check if a folder name is provided
if [ -z "$1" ]; then
    echo "Please provide a folder name."
    exit 1
fi

folder="$1"
i=0

# Process files in alphabetical order
for file in $(ls "$folder" | sort); do
    full_path="$folder/$file"
    
    # Extract year and month from the file name
    year="20${file:0:2}"
    month="${file:3:2}"
    
    # Default to January if month is not provided, invalid, or zero
    if ! [[ $month =~ ^[0-9]+$ ]] || [ "$month" -gt 12 ] || [ "$month" -eq 00 ]; then
        month=01
    fi

    # Forming the base date
    base_date_str="${year}-${month}-02 00:00:00 UTC"

    # Add i seconds to the base date
    new_date_str=$(date -d "$base_date_str + $i seconds" "+%Y%m%d%H%M.%S")

    # Check if date command succeeded
    if [ $? -ne 0 ]; then
        echo "Error processing date for file: $file"
        continue
    fi

    # Modify the creation and modification dates
    touch -t "$new_date_str" "$full_path"
    
    echo "$file: new date: $new_date_str"
    ((i++))
done
