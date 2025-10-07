# Usage Guide

## Quick Start

1. **Setup the Environment**
   ```bash
   # Linux/Mac
   ./setup_venv.sh
   
   # Windows
   setup_venv.bat
   ```

2. **Activate the Virtual Environment**
   ```bash
   # Linux/Mac
   source venv/bin/activate
   
   # Windows
   venv\Scripts\activate.bat
   ```

3. **Run the Application**
   ```bash
   python image_converter.py
   ```

## Using the GUI

### Step 1: Select Input File
Click the "Browse..." button in the **Input File** section to select an image file. 

Supported input formats:
- **Standard**: PNG, JPEG, GIF, BMP, TIFF, WebP, ICO
- **Optional** (requires libraries): HEIF/HEIC, SVG, PSD

### Step 2: Choose Output Format
Select the desired output format from the dropdown menu. Available formats:
- PNG
- JPEG
- WebP
- GIF
- BMP
- TIFF
- ICO
- EPS
- PDF (requires reportlab)
- HEIF/HEIC (requires pillow-heif)

### Step 3: Adjust Parameters

#### Quality (JPEG, WebP, HEIF/HEIC)
- Range: 1-100
- Higher = Better quality, larger file size
- Default: 95
- **When to adjust**: 
  - Use 85-95 for high-quality photos
  - Use 70-85 for web images
  - Use 50-70 for thumbnails

#### Compression (PNG)
- Range: 0-9
- Higher = More compression, smaller file size
- Default: 6
- **When to adjust**:
  - Use 9 for maximum compression (slower)
  - Use 0 for fastest conversion (larger files)

#### Resize Options
Enable the "Resize Image" checkbox to resize the image:
- **Width** and **Height**: Target dimensions in pixels
- **Maintain aspect ratio**: Keep original proportions (thumbnail mode)
  - If checked: Image will fit within the specified dimensions
  - If unchecked: Image will be stretched to exact dimensions

### Step 4: Select Output Location (Optional)
Click "Browse..." in the **Output File** section to choose where to save the converted image.

If you don't select an output location, the converted image will be saved:
- In the same directory as the input file
- With the same name but different extension

**Example**:
- Input: `/home/user/photos/vacation.jpg`
- Output format: `png`
- Auto output: `/home/user/photos/vacation.png`

### Step 5: Convert
Click the **Convert** button to start the conversion. 

A success message will appear when complete, showing the output file location.

## Tips and Tricks

### Format Conversion Recommendations

#### For Web Use
- **Convert to**: WebP or JPEG
- **Quality**: 80-85
- **Reason**: Good balance of quality and file size

#### For Transparency
- **Convert to**: PNG or WebP
- **Reason**: Supports alpha channel (transparency)

#### For Printing
- **Convert to**: TIFF or PNG
- **Compression**: Low (0-3 for PNG)
- **Reason**: Maximum quality preservation

#### For Email/Sharing
- **Convert to**: JPEG
- **Quality**: 75-85
- **Enable**: Resize (e.g., 1200x1200 with aspect ratio)
- **Reason**: Smaller file size for faster transfer

#### For Professional Work
- **Convert to**: PSD or TIFF
- **Reason**: Preserves all image data and supports layers (PSD)

### Common Conversions

1. **Photo to Web Image**
   - Input: Large camera photo (e.g., 4000x3000 JPEG)
   - Output format: WebP
   - Quality: 85
   - Resize: 1920x1080, maintain aspect ratio

2. **Logo with Transparency**
   - Input: PSD or PNG with transparency
   - Output format: PNG
   - No resize needed

3. **Screenshot to Document**
   - Input: PNG screenshot
   - Output format: PDF
   - Useful for creating multi-page documents

4. **RAW to Standard Format**
   - Input: HEIC (iPhone photos)
   - Output format: JPEG
   - Quality: 90

## Troubleshooting

### Error: "HEIF/HEIC support not available"
**Solution**: Install pillow-heif
```bash
pip install pillow-heif
```

### Error: "PDF support not available"
**Solution**: Install reportlab
```bash
pip install reportlab
```

### Error: "PSD support not available"
**Solution**: Install psd-tools
```bash
pip install psd-tools
```

### Error: "SVG support not available"
**Solution**: SVG requires system libraries (cairo). On Linux:
```bash
sudo apt-get install libcairo2-dev
pip install svglib
```

### Image Quality is Poor
- Increase the **Quality** slider (for JPEG/WebP)
- Decrease the **Compression** level (for PNG)
- Ensure you're not resizing too small

### File Size is Too Large
- Decrease the **Quality** slider
- Increase the **Compression** level (for PNG)
- Enable **Resize** to reduce dimensions
- Consider converting to WebP format

### Colors Look Wrong
Some formats don't support transparency. When converting RGBA images to formats like JPEG or BMP:
- The application automatically adds a white background
- To preserve transparency, use PNG or WebP

## Batch Conversion

For converting multiple files, you can:
1. Run the application multiple times
2. Or create a Python script using the same libraries

Example batch script:
```python
from PIL import Image
import os

input_dir = "input_folder"
output_dir = "output_folder"
output_format = "webp"

for filename in os.listdir(input_dir):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        input_path = os.path.join(input_dir, filename)
        output_filename = os.path.splitext(filename)[0] + f".{output_format}"
        output_path = os.path.join(output_dir, output_filename)
        
        img = Image.open(input_path)
        img.save(output_path, output_format.upper(), quality=85)
        print(f"Converted: {filename} -> {output_filename}")
```

## Keyboard Shortcuts

- **Tab**: Navigate between fields
- **Space**: Toggle checkboxes
- **Enter**: (when focused on Convert button) Execute conversion

## Supported Formats Details

| Format | Input | Output | Transparency | Notes |
|--------|-------|--------|--------------|-------|
| PNG    | ✓     | ✓      | ✓            | Best for graphics, screenshots |
| JPEG   | ✓     | ✓      | ✗            | Best for photos, no transparency |
| WebP   | ✓     | ✓      | ✓            | Modern web format, good compression |
| GIF    | ✓     | ✓      | Limited      | Supports animation (static only in this app) |
| BMP    | ✓     | ✓      | ✗            | Uncompressed, large files |
| TIFF   | ✓     | ✓      | ✓            | Professional, high quality |
| ICO    | ✓     | ✓      | ✓            | Windows icons |
| EPS    | ✗     | ✓      | ✗            | Vector format (rasterized) |
| PDF    | Limited | ✓    | ✗            | Document format |
| HEIF/HEIC | ✓  | ✓      | ✓            | iPhone photos, requires pillow-heif |
| SVG    | ✓     | ✗      | ✓            | Vector graphics, requires svglib |
| PSD    | ✓     | ✗      | ✓            | Photoshop files, requires psd-tools |
