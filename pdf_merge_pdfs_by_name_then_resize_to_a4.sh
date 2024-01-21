#!/bin/bash

# ---------------------------------------------------------------
# Purpose: This script finds all PDF files in a specified directory 
# (excluding files starting with 'out_' or 'resized_'), resizes them to A4 size,
# and then merges them into a single PDF file.
# Requirements: pdftk and Ghostscript must be installed.
# Usage:
#   1. Make sure pdftk and Ghostscript are installed on your system.
# sudo apt-get install pdftk
# sudo apt-get install ghostscript
#   2. Place this script in a desired directory.
#   3. Grant execute permissions to the script: chmod +x merge_and_resize_pdfs.sh
#   4. Run the script: ./merge_and_resize_pdfs.sh
# Output: A merged PDF file named 'resized_out_merged.pdf' will be created in the same directory.
# ---------------------------------------------------------------


# Set directory containing PDFs
pdf_dir="/home/feiyu/Downloads/materials"

# Output PDF file name
output_pdf="out_merged.pdf"

# Full path for the output PDF
output_path="$pdf_dir/$output_pdf"
resized_output_path="$pdf_dir/resized_$output_pdf"

# Find and sort PDF files while excluding ones starting with 'out_' or 'resized_'
# Store the list of files in an array
readarray -t pdf_files < <(find "$pdf_dir" -maxdepth 1 \( -iname "*.pdf" -o -iname "*.PDF" \) | grep -vE '/(out_|resized_)' | sort)

# Check if any PDF files are found
if [ ${#pdf_files[@]} -eq 0 ]; then
    echo "No PDF files to merge. Exiting."
    exit 1
fi

# Create an array to hold the paths of resized PDFs
resized_pdf_files=()

# Resize each PDF to A4 size and add it to the list of files to be merged
echo "Resizing PDF files to A4 size..."
for pdf_file in "${pdf_files[@]}"; do
    resized_pdf_file="$pdf_dir/resized_$(basename "$pdf_file")"
    gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/printer -dFIXEDMEDIA -dPDFFitPage -sPAPERSIZE=a4 -dNOPAUSE -dQUIET -dBATCH -sOutputFile="$resized_pdf_file" "$pdf_file"
    if [ $? -eq 0 ]; then
        resized_pdf_files+=("$resized_pdf_file")
    else
        echo "Failed to resize PDF file: $pdf_file"
    fi
done

# Check if any PDFs were resized successfully
if [ ${#resized_pdf_files[@]} -eq 0 ]; then
    echo "No PDF files were resized successfully. Exiting."
    exit 1
fi

# Merge resized PDF files
echo "Merging resized PDF files..."
pdftk "${resized_pdf_files[@]}" cat output "$resized_output_path"

# Check if pdftk command was successful
if [ ! -f "$resized_output_path" ]; then
    echo "PDF merging failed. Exiting."
    exit 1
fi

echo "PDFs resized to A4 size and merged. Output file: $resized_output_path"
