import os
from PIL import Image, ImageOps, ImageEnhance

def remove_background(image_path, tolerance=35):
    img = Image.open(image_path).convert("RGBA")
    data = img.getdata()
    
    # Sample background color from corners
    corner_colors = [
        data[0],
        data[img.width - 1],
        data[(img.height - 1) * img.width],
        data[img.height * img.width - 1]
    ]
    
    bg_r = sum(c[0] for c in corner_colors) / 4.0
    bg_g = sum(c[1] for c in corner_colors) / 4.0
    bg_b = sum(c[2] for c in corner_colors) / 4.0
    
    newData = []
    for item in data:
        r, g, b, a = item
        # Distance from background color
        dist = ((r - bg_r)**2 + (g - bg_g)**2 + (b - bg_b)**2) ** 0.5
        
        if dist < tolerance:
            # Fully transparent
            newData.append((255, 255, 255, 0))
        elif dist < tolerance + 25:
            # Smooth edge alpha transition
            alpha = int(255 * ((dist - tolerance) / 25.0))
            newData.append((r, g, b, alpha))
        else:
            newData.append((r, g, b, 255))
            
    img.putdata(newData)
    
    # Autocrop transparent borders
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
        
    return img

def create_walking_frames(base_img):
    # Frame 0: Idle Standing
    idle_frame = base_img.copy()
    
    # Frame 1: Walk Step Left (Slight tilt left + squeeze/stretch)
    w, h = base_img.size
    walk1 = base_img.rotate(6, expand=True, resample=Image.BICUBIC)
    
    # Frame 2: Walk Step Right (Slight tilt right + squeeze/stretch)
    walk2 = base_img.rotate(-6, expand=True, resample=Image.BICUBIC)
    
    return idle_frame, walk1, walk2

if __name__ == "__main__":
    source_cat_path = "/home/shogoyoshimura/.gemini/antigravity/brain/6daefbdd-e8c7-4911-b42b-cca283b4cb0d/cat_illustration_1785592511786.jpg"
    target_dir = "/home/shogoyoshimura/.gemini/antigravity/scratch/cute-cat-app/public/assets"
    
    print("Processing transparent cat images...")
    transparent_cat = remove_background(source_cat_path)
    
    idle, walk1, walk2 = create_walking_frames(transparent_cat)
    
    idle.save(os.path.join(target_dir, "cat.png"), "PNG")
    walk1.save(os.path.join(target_dir, "cat_walk1.png"), "PNG")
    walk2.save(os.path.join(target_dir, "cat_walk2.png"), "PNG")
    
    print("Successfully generated unified transparent PNG cat assets!")
