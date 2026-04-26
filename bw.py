import glob
import os
from PIL import Image

# Define the directory path where your JPEGs are located.
# Use '.' for the current directory or specify a full path (e.g., r'C:\Users\YourUser\Pictures')
ROOT="/home/lazarus/mormir_proj"
#for dir in "${ROOT}"/* do:
# Use glob to find all files ending with .jpg
jpeg_files = glob.glob(('./**/*.jpg'))
width = 384
for file in jpeg_files:
    print(file)
    try:
        im = Image.open(file)
        im.thumbnail((width, 9999))
        im.save(file)
    except Exception as e:
        print(f"Failed to open {file}: {e}")