import os
from PIL import Image, ImageDraw

def process_cat_pure_pil(image_path, tolerance=30):
    # Open source image
    img = Image.open(image_path).convert("RGBA")
    w, h = img.size
    
    # 1. Sample background color at (0, 0)
    bg_r, bg_g, bg_b, _ = img.getpixel((0, 0))
    
    # 2. Create a temporary mask image for Flood Fill
    # Mark pixels that match background color (within tolerance) as 255 (white), others 0 (black)
    mask = Image.new("L", (w, h), 0)
    img_rgb = img.convert("RGB")
    
    for y in range(h):
        for x in range(w):
            r, g, b = img_rgb.getpixel((x, y))
            dist = ((r - bg_r)**2 + (g - bg_g)**2 + (b - bg_b)**2) ** 0.5
            if dist < tolerance:
                mask.putpixel((x, y), 255)
                
    # 3. Perform Flood Fill ONLY from the 4 outer corners (0,0), (w-1,0), (0,h-1), (w-1,h-1)
    # FloodFill will mark only the CONTINUOUS OUTER background as 128
    outer_mask = Image.new("L", (w, h), 0)
    
    # Copy background candidate mask
    outer_draw = ImageDraw.Draw(mask)
    
    # We flood fill on a copy of mask using ImageDraw.floodfill
    # Floodfill converts contiguous 255 pixels from (0,0) into 128
    ImageDraw.floodfill(mask, (0, 0), 128)
    ImageDraw.floodfill(mask, (w - 1, 0), 128)
    ImageDraw.floodfill(mask, (0, h - 1), 128)
    ImageDraw.floodfill(mask, (w - 1, h - 1), 128)
    
    # 4. Now pixels with value 128 are OUTER BACKGROUND -> set alpha to 0
    # All other pixels (including cat's white body parts) remain alpha 255!
    result_data = []
    orig_pixels = img.getdata()
    mask_pixels = mask.getdata()
    
    for i, mask_val in enumerate(mask_pixels):
        r, g, b, a = orig_pixels[i]
        if mask_val == 128:
            result_data.append((255, 255, 255, 0)) # Outer background -> transparent
        else:
            result_data.append((r, g, b, 255)) # Cat body & internal white -> 100% SOLID OPAQUE
            
    img.putdata(result_data)
    
    # Crop transparent margins
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
        
    return img

def create_walking_frames(base_img):
    idle_frame = base_img.copy()
    walk1 = base_img.rotate(6, expand=True, resample=Image.BICUBIC)
    walk2 = base_img.rotate(-6, expand=True, resample=Image.BICUBIC)
    return idle_frame, walk1, walk2

if __name__ == "__main__":
    source_cat_path = "/home/shogoyoshimura/.gemini/antigravity/brain/6daefbdd-e8c7-4911-b42b-cca283b4cb0d/cat_illustration_1785592511786.jpg"
    target_dir = "/home/shogoyoshimura/.gemini/antigravity/scratch/cute-cat-app/public/assets"
    
    print("Running Pure PIL Flood-Fill Background Removal...")
    solid_cat = process_cat_pure_pil(source_cat_path, tolerance=35)
    
    idle, walk1, walk2 = create_walking_frames(solid_cat)
    
    idle.save(os.path.join(target_dir, "cat.png"), "PNG")
    walk1.save(os.path.join(target_dir, "cat_walk1.png"), "PNG")
    walk2.save(os.path.join(target_dir, "cat_walk2.png"), "PNG")
    
    print("Successfully generated 100% solid-body transparent cat PNGs!")
