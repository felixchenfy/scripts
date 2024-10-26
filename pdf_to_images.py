from pdf2image import convert_from_path

# Path to the uploaded PDF file
pdf_path = '/mnt/data/卖东西.pdf'

# Convert each page of the PDF to an image
images = convert_from_path(pdf_path)

# Save each image as a separate file
image_paths = []
for i, image in enumerate(images):
    image_path = f'/mnt/data/卖东西_page_{i+1}.png'
    image.save(image_path, 'PNG')
    image_paths.append(image_path)

image_paths
