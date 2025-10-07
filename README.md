# SimpleImageConverter

Simple image converter application with Python and Tkinter GUI.

## Features

- **Multiple Format Support**: Convert between various image formats including:
  - PNG, JPEG, WebP, EPS, PDF, TIFF, BMP, GIF, ICO
  - HEIF/HEIC (with pillow-heif)
  - SVG (with svglib)
  - PSD (with psd-tools)

- **Graphical User Interface**: Easy-to-use Tkinter-based GUI
  - File browser for selecting input/output files
  - Format selection dropdown
  - Automatic output to input file location if no output specified

- **Conversion Parameters**:
  - Quality control for JPEG and WebP (1-100)
  - Compression level for PNG (0-9)
  - Image resize options with aspect ratio maintenance
  - Format-specific parameters displayed dynamically

## Requirements

- Python 3.7 or higher
- tkinter (usually included with Python)

## Installation

### Quick Setup (Recommended)

#### Linux/Mac:
```bash
chmod +x setup_venv.sh
./setup_venv.sh
```

#### Windows:
```batch
setup_venv.bat
```

### Manual Setup

1. Create a virtual environment:
```bash
python3 -m venv venv
```

2. Activate the virtual environment:

**Linux/Mac:**
```bash
source venv/bin/activate
```

**Windows:**
```batch
venv\Scripts\activate.bat
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Activate the virtual environment (if not already activated):
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate.bat  # Windows
```

2. Run the application:
```bash
python image_converter.py
```

3. In the GUI:
   - Click "Browse..." in the Input File section to select an image
   - Select the output format from the dropdown
   - (Optional) Click "Browse..." in the Output File section to specify output location
   - Adjust conversion parameters as needed:
     - Quality for JPEG/WebP formats
     - Compression for PNG format
     - Resize options if needed
   - Click "Convert" to convert the image

## Supported Conversions

### Input Formats
- Standard: PNG, JPEG, GIF, BMP, TIFF, WebP, ICO
- Optional (with libraries): HEIF/HEIC, SVG, PSD

### Output Formats
- Standard: PNG, JPEG, GIF, BMP, TIFF, WebP, ICO, EPS
- Optional (with libraries): HEIF/HEIC, PDF

## Parameters

### Quality (1-100)
- Applies to: JPEG, WebP, HEIF/HEIC
- Higher values = better quality, larger file size
- Default: 95

### Compression (0-9)
- Applies to: PNG
- Higher values = more compression, smaller file size
- Default: 6

### Resize
- Optional image resizing with width and height
- Can maintain aspect ratio (thumbnail) or stretch to exact dimensions

## Dependencies

### Required
- Pillow: Core image processing library

### Optional
- pillow-heif: HEIF/HEIC format support
- reportlab: PDF output support
- svglib: SVG input support
- psd-tools: PSD input support

## License

MIT License

## Testing

To verify the application structure without installing all dependencies:
```bash
python3 verify_structure.py
```

This checks:
- Python syntax validity
- Code structure (classes, methods, functions)
- Required imports and files

For batch conversion examples without GUI:
```bash
python3 example_batch.py
```

## Development

This application uses:
- Python 3 for development
- Virtual environment (venv) for dependency isolation
- Tkinter for the graphical interface
- Pillow (PIL) as the core image processing library
