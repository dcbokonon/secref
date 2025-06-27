#!/usr/bin/env python3
"""Create simple icon files for PWA manifest"""

from PIL import Image, ImageDraw, ImageFont

# Create icons with SecRef branding
sizes = [192, 512]
bg_color = (0, 0, 0)  # Black background
text_color = (0, 255, 0)  # Green text
border_color = (0, 255, 0)  # Green border

for size in sizes:
    # Create new image
    img = Image.new('RGB', (size, size), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Draw border
    border_width = size // 20
    draw.rectangle(
        [border_width, border_width, size - border_width, size - border_width],
        outline=border_color,
        width=border_width
    )
    
    # Draw "SR" text
    font_size = size // 3
    try:
        # Try to use a monospace font
        font = ImageFont.truetype("/System/Library/Fonts/Courier.dfont", font_size)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    text = "SR"
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center the text
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    draw.text((x, y), text, fill=text_color, font=font)
    
    # Save the image
    img.save(f'public/icon-{size}.png')
    print(f"Created icon-{size}.png")

print("Icons created successfully!")