import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

def precise_background_removal(image_path, tolerance=30):
    # Open image as RGBA
    img = Image.open(image_path).convert("RGBA")
    w, h = img.size
    
    # Convert to RGB array for distance calculation
    rgb_arr = np.array(img.convert("RGB"), dtype=np.int32)
    
    # Sample average corner color (background color)
    corners = [
        rgb_arr[0, 0],
        rgb_arr[0, w - 1],
        rgb_arr[h - 1, 0],
        rgb_arr[h - 1, w - 1]
    ]
    bg_color = np.mean(corners, axis=0)
    
    # Calculate color distance map from background color
    diff = np.sqrt(np.sum((rgb_arr - bg_color) ** 2, axis=2))
    
    # Create binary background candidates mask (True = background-like)
    bg_candidate_mask = (diff < tolerance)
    
    # Create mask image for Flood Fill (1-bit mask)
    # Start flood fill from the 4 corners so only CONNECTED outer background is filled
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    
    # Fill background region starting from border points
    # First, draw candidate background pixels as white (255)
    mask_arr = np.where(bg_candidate_mask, 255, 0).astype(np.uint8)
    mask_img = Image.fromarray(mask_arr, mode="L")
    
    # Floodfill from edges on mask_img
    # We create an outer-only mask
    outer_mask = Image.new("L", (w + 2, h + 2), 0)
    outer_arr = np.zeros((h + 2, w + 2), dtype=np.uint8)
    outer_arr[1:-1, 1:-1] = np.where(bg_candidate_mask, 255, 0)
    
    # Perform flood fill from (0,0) on mask
    flood_img = Image.fromarray(outer_arr, mode="L")
    ImageDraw.floodfill(flood_img, (0, 0), 128)
    
    # The flood-filled region (128) is guaranteed to be the OUTER connected background
    flood_arr = np.array(flood_img)
    is_outer_bg = (flood_arr[1:-1, 1:-1] == 128)
    
    # Create final RGBA image
    img_arr = np.array(img)
    
    # Set alpha: 0 for outer background, 255 for cat body
    img_arr[is_outer_bg, 3] = 0
    img_arr[~is_outer_bg, 3] = 255
    
    final_img = Image.fromarray(img_arr, mode="RGBA")
    
    # Autocrop transparent margin
    bbox = final_img.getbbox()
    if bbox:
        final_img = final_img.crop(bbox)
        
    return final_img

def create_walking_frames(base_img):
    idle_frame = base_img.copy()
    
    # Walk Frame 1: Tilt 6 deg
    walk1 = base_img.rotate(6, expand=True, resample=Image.BICUBIC)
    
    # Walk Frame 2: Tilt -6 deg
    walk2 = base_img.rotate(-6, expand=True, resample=Image.BICUBIC)
    
    return idle_frame, walk1, walk2

if __name__ == "__main__":
    source_cat_path = "/home/shogoyoshimura/.gemini/antigravity/brain/6daefbdd-e8c7-4911-b42b-cca283b4cb0d/cat_illustration_1785592511786.jpg"
    target_dir = "/home/shogoyoshimura/.gemini/antigravity/scratch/cute-cat-app/public/assets"
    
    print("Executing flood-fill outer background removal...")
    solid_cat = precise_background_removal(source_cat_path, tolerance=32)
    
    idle, walk1, walk2 = create_walking_frames(solid_cat)
    
    idle.save(os.path.join(target_dir, "cat.png"), "PNG")
    walk1.save(os.path.join(target_dir, "cat_walk1.png"), "PNG")
    walk2.save(os.path.join(target_dir, "cat_walk2.png"), "PNG")
    
    print("Successfully produced solid non-transparent cat body PNGs!")
