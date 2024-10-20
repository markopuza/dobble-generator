import os
import sys
import math
import numpy as np
from PIL import Image, ImageDraw
from random import randint, shuffle

# Configuration
CANVAS_SIZE = (1000, 1000)
CIRCLE_RADIUS = 500
CENTER = (CANVAS_SIZE[0] // 2, CANVAS_SIZE[1] // 2)
EVOLUTION_ITERATIONS = 2000


INPUT_FOLDER = 'img_preprocessed'
OUTPUT_FOLDER = 'cards'

def progress_bar(progress, total):
    bar_length = 40
    block = int(round(bar_length * progress / total))
    progress_percentage = round(progress / total * 100, 1)
    bar = "#" * block + "-" * (bar_length - block)
    sys.stdout.write(f"\r[{bar}] {progress_percentage}%")
    sys.stdout.flush()

def load_images(image_paths):
    """Load images and convert them to RGBA format."""
    images = []
    for path in image_paths:
        img = Image.open(path).convert("RGBA")
        images.append(img)
    return images

def get_mask(image):
    """Get the alpha mask of the image as a numpy array."""
    return np.array(image.split()[-1]) > 0

def scale_image(image, scale):
    """Scale the image by the given factor."""
    new_size = (int(image.size[0] * scale), int(image.size[1] * scale))
    return image.resize(new_size, Image.Resampling.LANCZOS)

def rotate_image(image, angle):
    """Rotate the image by the given angle."""
    return image.rotate(angle, expand=True)

def is_within_circle(position, image_size, center, radius):
    """Check if the image at the given position is entirely within the circle."""
    x, y = position
    w, h = image_size
    corners = [
        (x, y),
        (x + w, y),
        (x, y + h),
        (x + w, y + h)
    ]
    for corner in corners:
        dx = corner[0] - center[0]
        dy = corner[1] - center[1]
        if math.hypot(dx, dy) > radius:
            return False
    return True

def check_overlap(new_mask, new_position, placed_masks, canvas_size):
    """Check if the new mask at the given position overlaps with any existing masks."""
    new_x, new_y = new_position
    new_h, new_w = new_mask.shape

    # Initialize a blank canvas mask
    canvas_mask = np.zeros(canvas_size, dtype=bool)

    # Paste existing masks onto the canvas mask
    for mask, pos in placed_masks:
        x, y = pos
        # Determine the region where the mask will be placed
        x_end = min(x + mask.shape[1], canvas_size[1])
        y_end = min(y + mask.shape[0], canvas_size[0])
        x_start = max(x, 0)
        y_start = max(y, 0)

        mask_x_start = max(0, -x)
        mask_y_start = max(0, -y)
        mask_x_end = mask_x_start + (x_end - x_start)
        mask_y_end = mask_y_start + (y_end - y_start)

        if mask_x_end > mask.shape[1] or mask_y_end > mask.shape[0]:
            continue  # Skip if mask goes out of canvas bounds

        canvas_mask[y_start:y_end, x_start:x_end] |= mask[mask_y_start:mask_y_end, mask_x_start:mask_x_end]

    # Determine the region for the new mask
    x_end = min(new_x + new_w, canvas_size[1])
    y_end = min(new_y + new_h, canvas_size[0])
    x_start = max(new_x, 0)
    y_start = max(new_y, 0)

    mask_x_start = max(0, -new_x)
    mask_y_start = max(0, -new_y)
    mask_x_end = mask_x_start + (x_end - x_start)
    mask_y_end = mask_y_start + (y_end - y_start)

    if mask_x_end > new_mask.shape[1] or mask_y_end > new_mask.shape[0]:
        # Part of the mask is outside the canvas; treat it as overlapping
        return True

    # Check for overlap
    overlap = canvas_mask[y_start:y_end, x_start:x_end] & new_mask[mask_y_start:mask_y_end, mask_x_start:mask_x_end]
    return np.any(overlap)

def scale_images(images, positions, angles, scales, canvas_size, center, radius):
    """Autoscale images to fit within the circle with no overlap and minimum distance."""
    placed = []  # List of tuples (mask, position)
    scaled_images = []

    for idx, (img, position, angle, scale) in enumerate(zip(images, positions, angles, scales)):
        mask = None
        
        # Scale and rotate the image
        scaled_img = scale_image(img, scale)
        rotated_img = rotate_image(scaled_img, angle)
        mask = get_mask(rotated_img)
        img_size = rotated_img.size  # (width, height)
        
        # Check if the image fits within the circle and does not overlap
        if is_within_circle(position, img_size, center, radius) and not check_overlap(mask, position, placed, canvas_size[::-1]):
            placed.append((mask, position))
            scaled_images.append(rotated_img)
        else:
            raise RuntimeError(f"Failed to place image {idx + 1} without overlap.")
    
    return scaled_images

def composite_images(images, positions):
    """Compose the final image on the canvas."""
    canvas = Image.new("RGBA", CANVAS_SIZE, (255, 255, 255, 0))
    draw = ImageDraw.Draw(canvas)

    # Draw the big canvas circle (in white)
    draw.ellipse(
        [(CENTER[0] - CIRCLE_RADIUS, CENTER[1] - CIRCLE_RADIUS),
         (CENTER[0] + CIRCLE_RADIUS, CENTER[1] + CIRCLE_RADIUS)],
        fill="white", outline="white", width=5
    )

    for img, position in zip(images, positions):
        canvas.paste(img, position, img)
    return canvas

def display_images(image_paths, positions, angles, scales, actually_display=False):
    """Main function to autoscale images, ensure no overlap, and display the result."""
    images = load_images(image_paths)
    scaled_images = scale_images(images, positions, angles, scales, CANVAS_SIZE, CENTER, CIRCLE_RADIUS)
    final_image = composite_images(scaled_images, positions)
    if actually_display:
        final_image.show()
    return final_image

def evolve_card(image_paths, iterations, cardname, save=False, symbols=8):
    """ 
    Given symbols as image paths, and a number of iterations for the evolution process, generates a card.
    
    The evolution process consists of randomly wigling the symbols around the card (using random rotations,
    repositioning and rescaling).
    """
    positions = [(200, 200), (400, 200), (600, 200), (100, 400),
             (300, 400), (500, 400), (700, 400), (500, 600)][:symbols]
    angles = [0, 45, 90, 135, 180, 225, 270, 315][:symbols]
    shuffle(positions)
    shuffle(angles)
    scales = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1][:symbols]
    final_card = None

    for iteration in range(iterations):
        progress_bar(iteration, iterations)
        orig_pos, orig_ang, orig_scale = list(positions), list(angles), list(scales)

        x = randint(1, 10)
        if x == 1:
            # random rotation
            angles[ randint(0, len(angles) - 1) ] += randint(-10, 10)
        elif x < 5:
            # random rescaling
            scales[ randint(0, len(scales) - 1) ] *= 1.0 + randint(-1, 10) / 10.0
        else:
            # random reposition
            i = randint(0, len(positions) - 1)
            px, py = positions[i]
            px += randint(-10, 10)
            py += randint(-10, 10)
            positions[i] = (px, py)

        # print(f'Iteration {1 + iteration}')
        try:
            final_card = display_images(image_paths, positions, angles, scales)
            # print('New mod successful')
        except:
            positions, angles, scales = orig_pos, orig_ang, orig_scale
            # print('New mod failed')
            pass
    
    if not save:
        final_card.show()
    else:
        output_path = os.path.join(OUTPUT_FOLDER, cardname) + '.png'
        final_card.save(output_path, "PNG")
    return final_card, positions, angles, scales

def generate_cards(symbols=8):
    '''Generates lists of numerical representations of symbols that should appear on cards.'''
    n = symbols - 1 # should be prime
    cards = [[1] for _ in range(n+1)]

    for i in range(n+1):
        for j in range(n):
            cards[i].append(j+2 + i*n)
    for i in range(n):
        for j in range(n):
            cards.append([i + 2])
            for k in range(n):
                cards[len(cards)-1].append(n+2 + n*k + (i*k+j)%n)
    return cards


image_names = {
    int(f.split('_')[0]): os.path.join(INPUT_FOLDER, f) for f in os.listdir(INPUT_FOLDER) if f.endswith('.png')
}
cards = generate_cards()

for i, c in enumerate(cards, 1):
    print(f'\nEvolving card {i}')
    evolve_card([image_names[x] for x in c], EVOLUTION_ITERATIONS, f'card_{i}', save=True)