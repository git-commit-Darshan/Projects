#!/usr/bin/env python3
"""
generate_apriltag.py

Download a pre-generated AprilTag marker, scale it to a desired pixel size,
add the correct border width, and save it for printing.
"""

import argparse
import requests
from PIL import Image
from io import BytesIO

def fetch_and_create_apriltag(family: str, tag_id: int, size_px: int, border_bits: int, output: str):
    # Parse family string, e.g. "tag36h11" → bits1=36, bits2=11
    bits1, bits2 = map(int, family[3:].split('h'))
    # GitHub filenames are zero-padded to 5 digits, and use an underscore between bits
    filename = f"tag{bits1}_{bits2}_{tag_id:05d}.png"
    url = f"https://raw.githubusercontent.com/AprilRobotics/apriltag-imgs/master/{family}/{filename}"
    
    # Download the image
    resp = requests.get(url)
    resp.raise_for_status()
    tag_img = Image.open(BytesIO(resp.content)).convert("RGB")
    
    # Compute size of the inner marker (excluding border)
    # In the repo, each PNG is exactly bits1 × bits1 pixels (no border)
    unit = size_px / (bits1 + 2 * border_bits)
    inner_size = int(bits1 * unit)
    border_px = int(border_bits * unit)
    
    # Resize inner marker, then paste into a new black canvas
    tag_img = tag_img.resize((inner_size, inner_size), Image.NEAREST)
    canvas = Image.new("RGB", (size_px, size_px), "black")
    canvas.paste(tag_img, (border_px, border_px))
    
    # Save result
    canvas.save(output)
    print(f"Saved AprilTag {family} id={tag_id} → {output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate an AprilTag image for printing.")
    parser.add_argument("family", help="Tag family (e.g. tag36h11)")
    parser.add_argument("tag_id", type=int, help="Tag ID (integer)")
    parser.add_argument("size_px", type=int, help="Total image size in pixels (including border)")
    parser.add_argument("--border", type=int, default=1, help="Border width in 'bits' (default: 1)")
    parser.add_argument("-o", "--output", default="apriltag.png", help="Output filename")
    args = parser.parse_args()
    fetch_and_create_apriltag(args.family, args.tag_id, args.size_px, args.border, args.output)
