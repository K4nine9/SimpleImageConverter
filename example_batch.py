#!/usr/bin/env python3
"""
Example: Batch Image Conversion Script

This script demonstrates how to convert multiple images programmatically
without using the GUI interface.

Usage:
    python example_batch.py

Requirements:
    pip install Pillow
"""

from PIL import Image
import os
import glob

def convert_images_batch(input_pattern, output_format, output_dir=None, quality=85, resize=None):
    """
    Convert multiple images to a specified format

    Args:
        input_pattern (str): Glob pattern for input files (e.g., "images/*.jpg")
        output_format (str): Output format (e.g., "webp", "png", "jpeg")
        output_dir (str, optional): Output directory. If None, use same as input
        quality (int): Quality for JPEG/WebP (1-100)
        resize (tuple, optional): Target size as (width, height) to resize images

    Returns:
        list: List of successfully converted files
    """
    # Find all matching files
    input_files = glob.glob(input_pattern)

    if not input_files:
        print(f"No files found matching pattern: {input_pattern}")
        return []

    print(f"Found {len(input_files)} files to convert")

    converted_files = []

    for input_path in input_files:
        try:
            # Load image
            img = Image.open(input_path)
            print(f"Processing: {os.path.basename(input_path)} ({img.size}, {img.mode})")

            # Apply resize if requested
            if resize:
                img.thumbnail(resize, Image.Resampling.LANCZOS)
                print(f"  Resized to: {img.size}")

            # Determine output path
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                output_filename = os.path.splitext(os.path.basename(input_path))[0] + f".{output_format}"
                output_path = os.path.join(output_dir, output_filename)
            else:
                input_dir = os.path.dirname(input_path) or "."
                output_filename = os.path.splitext(os.path.basename(input_path))[0] + f".{output_format}"
                output_path = os.path.join(input_dir, output_filename)

            # Convert based on format
            output_format_upper = output_format.upper()

            # Handle formats that don't support transparency
            if output_format.lower() in ['jpg', 'jpeg', 'bmp'] and img.mode in ('RGBA', 'LA'):
                # Create white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background

            # Save image
            save_kwargs = {}
            if output_format.lower() in ['jpg', 'jpeg']:
                save_kwargs = {'quality': quality, 'optimize': True}
            elif output_format.lower() == 'webp':
                save_kwargs = {'quality': quality}
            elif output_format.lower() == 'png':
                save_kwargs = {'compress_level': 6}

            img.save(output_path, output_format_upper, **save_kwargs)

            # Get file sizes
            input_size = os.path.getsize(input_path)
            output_size = os.path.getsize(output_path)
            reduction = (1 - output_size / input_size) * 100

            print(f"  Saved: {output_path}")
            print(f"  Size: {input_size:,} bytes -> {output_size:,} bytes ({reduction:+.1f}%)")

            converted_files.append(output_path)

        except Exception as e:
            print(f"  ERROR converting {input_path}: {e}")

    return converted_files

def example_1_photos_to_webp():
    """Example 1: Convert photos to WebP format"""
    print("\n" + "=" * 60)
    print("Example 1: Convert Photos to WebP")
    print("=" * 60)

    # Convert all JPEGs in a folder to WebP
    converted = convert_images_batch(
        input_pattern="sample_images/*.jpg",  # Adjust path as needed
        output_format="webp",
        quality=85,
        resize=(1920, 1080)  # Resize to Full HD
    )

    print(f"\nConverted {len(converted)} files")

def example_2_png_to_jpeg():
    """Example 2: Convert PNG to JPEG with white background"""
    print("\n" + "=" * 60)
    print("Example 2: Convert PNG to JPEG")
    print("=" * 60)

    converted = convert_images_batch(
        input_pattern="screenshots/*.png",
        output_format="jpeg",
        output_dir="output_jpeg",
        quality=90
    )

    print(f"\nConverted {len(converted)} files")

def example_3_create_thumbnails():
    """Example 3: Create thumbnails"""
    print("\n" + "=" * 60)
    print("Example 3: Create Thumbnails")
    print("=" * 60)

    converted = convert_images_batch(
        input_pattern="photos/*.*",
        output_format="jpeg",
        output_dir="thumbnails",
        quality=75,
        resize=(320, 320)
    )

    print(f"\nCreated {len(converted)} thumbnails")

def create_sample_images():
    """Create sample images for demonstration"""
    print("Creating sample images for demonstration...")

    os.makedirs("sample_images", exist_ok=True)

    # Create a few sample images
    colors = [
        ('red', (255, 0, 0)),
        ('green', (0, 255, 0)),
        ('blue', (0, 0, 255)),
        ('yellow', (255, 255, 0))
    ]

    for name, color in colors:
        img = Image.new('RGB', (800, 600), color)
        path = f"sample_images/{name}.jpg"
        img.save(path, 'JPEG', quality=95)
        print(f"  Created: {path}")

    # Create one with transparency
    img_rgba = Image.new('RGBA', (400, 400), (255, 0, 0, 128))
    path = "sample_images/transparent.png"
    img_rgba.save(path, 'PNG')
    print(f"  Created: {path}")

    print("Sample images created!\n")

def main():
    """Main function"""
    print("=" * 60)
    print("Batch Image Conversion Examples")
    print("=" * 60)

    # Check if PIL is available
    try:
        from PIL import Image
    except ImportError:
        print("\nError: Pillow is not installed")
        print("Please install it with: pip install Pillow")
        return 1

    # Create sample images if they don't exist
    if not os.path.exists("sample_images"):
        create_sample_images()

    # Run examples (commented out - uncomment to use)
    print("\nTo run examples, uncomment the desired example in the script:")
    print("  - example_1_photos_to_webp(): Convert photos to WebP")
    print("  - example_2_png_to_jpeg(): Convert PNG to JPEG")
    print("  - example_3_create_thumbnails(): Create thumbnails")

    # Uncomment to run:
    # example_1_photos_to_webp()
    # example_2_png_to_jpeg()
    # example_3_create_thumbnails()

    # Simple demo with sample images
    print("\nRunning demo with sample images...")
    converted = convert_images_batch(
        input_pattern="sample_images/*.jpg",
        output_format="webp",
        quality=85
    )

    if converted:
        print(f"\n✓ Successfully converted {len(converted)} files")
        print("\nCheck the 'sample_images' directory for output files")
    else:
        print("\n○ No files were converted (this is normal if sample_images is empty)")

    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        exit_code = 130
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        exit_code = 1

    exit(exit_code)
