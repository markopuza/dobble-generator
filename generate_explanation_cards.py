from PIL import Image, ImageDraw, ImageFont
import os
import re

# Load descriptions from symbols.txt
descriptions = []
with open('symbols.txt', 'r') as f:
    for line in f:
        if line.startswith('>'):
            parts = line.split('. ')
            if len(parts) == 2:
                descriptions.append(parts[1].strip())

# Get list of images from the 'img_preprocessed' folder and sort by numerical prefix
image_folder = 'img_preprocessed'
output_folder = 'cards'
os.makedirs(output_folder, exist_ok=True)
image_files = sorted([f for f in os.listdir(image_folder) if f.endswith('.png')],
                     key=lambda x: int(re.search(r'(\d+)', x).group(1)))

# Zip image files with descriptions
images_and_descriptions = list(zip(image_files, descriptions))

# Parameters
circle_diameter = 500
icon_size = 40  # Adjusted icon size to fit columns
font_size = 12  # Font size for text labels
padding = 5  # Padding between icons and text
left_margin = 25  # Extra margin for the leftmost column
font_path = '/path/to/font.ttf'  # Path to a font file (adjust accordingly)
adjust = 13

# Split images and descriptions into 3 groups
group_size = len(images_and_descriptions) // 3
image_groups = [images_and_descriptions[i:i + group_size] for i in range(0, len(images_and_descriptions), group_size)]

def generate_card(images_with_desc, card_num):
    # Create a blank card with white background
    card = Image.new('RGBA', (circle_diameter, circle_diameter), (255, 255, 255, 0))
    draw = ImageDraw.Draw(card)

    # Draw a white circle as the card background
    draw.ellipse([(0, 0), (circle_diameter, circle_diameter)], fill='white')

    # Use default font (remove font_path dependency if using load_default)
    font = ImageFont.load_default()

    # Define three columns: 5, 9, and 5 items
    col_counts = [5, 9, 5]
    row_height = (circle_diameter - padding * 4) // max(col_counts)  # Uniform row height for all columns

    # Column positions: left (with margin), center, right
    col_x_positions = [left_margin, circle_diameter // 3 + padding // 2, 2 * circle_diameter // 3 + padding // 2]

    for col_idx, (col_x, items_in_col) in enumerate(zip(col_x_positions, col_counts)):
        # Center the column vertically
        total_items_height = items_in_col * row_height
        start_y = (circle_diameter - total_items_height) // 2

        for row_idx in range(items_in_col):
            # Get the current image and description
            img_idx = sum(col_counts[:col_idx]) + row_idx
            img_name, desc = images_with_desc[img_idx]

            # Load the image and resize it to icon size
            img = Image.open(os.path.join(image_folder, img_name)).convert("RGBA")
            img = img.resize((icon_size, icon_size))

            # Calculate the y-position for this row
            row_y = start_y + row_idx * row_height

            # Paste the icon in the correct position
            card.paste(img, (col_x + adjust, row_y), img)

            # Draw the description label to the right of the icon
            text_x = col_x + icon_size + padding
            text_y = row_y + icon_size // 4  # Adjust to align text with the icon
            draw.text((text_x + adjust, text_y), desc, font=font, fill=(0, 0, 0))

    # Save the card
    card.save(f'{output_folder}/explanation_card_{card_num}.png', 'PNG')

# Generate all cards
for i, group in enumerate(image_groups):
    generate_card(group, i + 1)
