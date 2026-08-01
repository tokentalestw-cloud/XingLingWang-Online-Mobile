# -*- coding: utf-8 -*-
import sys
from PIL import Image

def generate_icons():
    sys.stdout.reconfigure(encoding='utf-8')
    src_path = 'C:/Users/a2132/.gemini/antigravity/brain/bccfde50-ebcc-4b3b-8cae-ba8bd4474145/media__1785548226160.jpg'
    
    img = Image.open(src_path)
    w, h = img.size
    print(f"Source image dimensions: {w}x{h}")
    
    # Crop to a square centered but offset slightly upwards (to capture the character's face beautifully)
    sq_size = min(w, h)
    
    # Calculate offset: center is (h - w) / 2. We shift it slightly up by offset factor.
    # The character's face is in the upper-mid region. Let's crop from y = (h - w) * 0.25 to y = y + w
    y0 = int((h - sq_size) * 0.25)
    y1 = y0 + sq_size
    x0 = 0
    x1 = sq_size
    
    cropped_img = img.crop((x0, y0, x1, y1))
    print(f"Cropped to square: {sq_size}x{sq_size} starting from y={y0}")
    
    # Save as 192x192 and 512x512 PNGs
    cropped_img.resize((192, 192), Image.Resampling.LANCZOS).save('static/icon-192.png', 'PNG')
    cropped_img.resize((512, 512), Image.Resampling.LANCZOS).save('static/icon-512.png', 'PNG')
    print("Successfully generated static/icon-192.png and static/icon-512.png!")

if __name__ == '__main__':
    generate_icons()
