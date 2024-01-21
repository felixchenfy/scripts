import os
from PIL import Image

dir = "/home/feiyu/Downloads/photos/"

def convert_images_to_pdf(directory):
    # Change the current directory to the given directory
    os.chdir(directory)

    # Iterate over all the files in the directory
    for file in os.listdir(directory):
        # Check if the file is a JPG image
        if file.lower().endswith('.jpg'):
            # Open the image using PIL
            image = Image.open(file)
            # Converting the image to RGB mode if it's not (required for conversion)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            # Define the PDF filename based on the JPG filename
            pdf_filename = f"{os.path.splitext(file)[0]}.pdf"
            # Save the image as a PDF
            image.save(pdf_filename)
            print(f"Converted {file} to {pdf_filename}")

convert_images_to_pdf(dir)
