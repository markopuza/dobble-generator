from PIL import Image, ImageDraw, ImageOps
import os

# Parameters to adjust
background_color = (160, 20, 20)  # Light red (RGB)
border_color = (20, 20, 20)  # White border color (RGB)
border_width = 20  # Width of the inside border
image_1_position = (150, 100)  # Position of the first image (x, y)
image_2_position = (110, 250)  # Position of the second image (x, y)
image_1_scale = 0.12  # Scale factor for the first image
image_2_scale = 0.75  # Scale factor for the second image
circle_diameter = 500  # Diameter of the card
image_folder = 'imgassets'  # Folder containing the images
image_1_name = 'kefear.png'  # Name of the first image
image_2_name = 'santa-old.png'  # Name of the second image

# Create output folder if it doesn't exist
output_folder = 'cards'
os.makedirs(output_folder, exist_ok=True)

# Create a blank image (card) with a transparent background (RGBA)
card = Image.new('RGBA', (circle_diameter, circle_diameter), (255, 255, 255, 0))
draw = ImageDraw.Draw(card)

# Draw the outer circle (the background with border)
draw.ellipse([(0, 0), (circle_diameter, circle_diameter)], fill=border_color)

# Draw the inner circle (the background without border)
inner_diameter = circle_diameter - 2 * border_width
draw.ellipse([(border_width, border_width), (border_width + inner_diameter, border_width + inner_diameter)], fill=background_color)

# Load and process the first image
img1 = Image.open(os.path.join(image_folder, image_1_name)).convert("RGBA")
# Resize the first image based on the scale factor
img1 = img1.resize((int(img1.width * image_1_scale), int(img1.height * image_1_scale)), Image.LANCZOS)
# Paste the first image on the card at the specified position
card.paste(img1, image_1_position, img1)

# Load and process the second image
img2 = Image.open(os.path.join(image_folder, image_2_name)).convert("RGBA")
# Resize the second image based on the scale factor
img2 = img2.resize((int(img2.width * image_2_scale), int(img2.height * image_2_scale)), Image.LANCZOS)
# Paste the second image on the card at the specified position
card.paste(img2, image_2_position, img2)

# Save the final card image
card.save(f'{output_folder}/backside.png', 'PNG')

print(f"Card saved as '{output_folder}/backside.png'")