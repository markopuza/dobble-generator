import os
from PIL import Image, ImageOps, ImageFilter
import numpy as np

input_folder = 'img'
output_folder = 'img_preprocessed'
os.makedirs(output_folder, exist_ok=True)
TARGET_WIDHT = 400

def crop_to_mask(image):
    """Crop the image to remove empty margins based on the alpha mask."""
    image = image.convert("RGBA")
    
    # Get the alpha channel (mask) as a numpy array
    mask = np.array(image.split()[-1])  # Alpha channel
    non_empty_pixels = np.where(mask > 0)

    # Get the bounding box
    top, bottom = np.min(non_empty_pixels[0]), np.max(non_empty_pixels[0])
    left, right = np.min(non_empty_pixels[1]), np.max(non_empty_pixels[1])
    
    # Crop the image to the bounding box
    return image.crop((left, top, right + 1, bottom + 1))

def preprocess_image(image_path, output_path, target_width=TARGET_WIDHT):
    """Preprocess the image: resize, add cushion, add white contour, and crop final image."""
    image = Image.open(image_path).convert("RGBA")  # Ensure the image is in RGBA mode
    
    # Resize to the targets, maintaining aspect ratio
    aspect_ratio = image.height / image.width
    new_height = int(target_width * aspect_ratio)
    resized_image = image.resize((target_width, new_height), Image.Resampling.LANCZOS)
 
    # Crop the image
    final_cropped_image = crop_to_mask(resized_image)

    # Save the processed image to the output folder
    final_cropped_image.save(output_path, "PNG")

def process_all_images(input_folder, output_folder):
    """Process all images in the input folder and save them to the output folder."""
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)
            preprocess_image(input_path, output_path)
            print(f"Processed: {filename}")

process_all_images(input_folder, output_folder)
