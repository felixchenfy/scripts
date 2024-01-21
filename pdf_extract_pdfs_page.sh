#!/bin/bash

# README
# Description:
#   This script processes PDF extraction based on instructions provided in a text string.
#   Each line in the string should contain three parts:
#     1. Input PDF file name
#     2. Output PDF file name
#     3. A list of page numbers to extract, separated by commas
#   The script reads the instructions and uses pdftk to extract the specified pages
#   from the input PDF and save them as a new PDF file. If the output file already
#   exists, it will be overwritten.
#   The input and output PDF file names are relative to the directory defined in the script.
#
# Usage:
#   1. Ensure pdftk is installed on your system. If not, you can install it using:
#      - Debian/Ubuntu: sudo apt-get install pdftk
#      - Red Hat/Fedora/CentOS: sudo yum install pdftk
#   2. Define the directory path and instructions string in the script.
#   3. Give execution permission to the script: chmod +x script_name.sh
#   4. Run the script: ./script_name.sh

# Define the directory path
directory_path="/home/feiyu/Downloads/"

# Define the instructions as a multi-line string
instructions="
resized_out_merged.pdf extracted.pdf 1,2
"

# Process each line in the instructions string
while IFS= read -r line
do
    # Skip empty lines
    [ -z "$line" ] && continue

    # Read the input filename, output filename, and pages from the line
    IFS=' ' read -r -a array <<< "$line"
    input_pdf="${array[0]}"
    output_pdf="${array[1]}"
    pages=${array[@]:2} # Get the rest of the array elements (page numbers)
    pages=$(echo $pages | tr ',' ' ') # Replace commas with spaces for pdftk

    # Construct full paths for the input and output PDF files
    full_input_pdf="$directory_path/$input_pdf"
    full_output_pdf="$directory_path/$output_pdf"

    # Check if input PDF file exists
    if [ ! -f "$full_input_pdf" ]; then
        echo "Error: Input file $full_input_pdf does not exist."
        continue
    fi

    # Run pdftk to extract the specified pages
    pdftk "$full_input_pdf" cat $pages output "$full_output_pdf"

    # Check if pdftk ran successfully
    if [ $? -ne 0 ]; then
        echo "Error: pdftk failed to process $full_input_pdf."
        continue
    fi

    echo "Successfully created $full_output_pdf from $full_input_pdf."
done <<< "$instructions"
