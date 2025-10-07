#!/usr/bin/env python3
"""
Test script for image converter
This script validates the image converter structure and basic functionality
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test if required modules can be imported"""
    print("Testing imports...")
    
    try:
        import tkinter as tk
        print("✓ tkinter imported successfully")
    except ImportError as e:
        print(f"○ tkinter not available (usually comes with Python, install python3-tk)")
        print(f"  This is expected in headless environments")
    
    try:
        from PIL import Image
        print(f"✓ Pillow imported successfully")
    except ImportError as e:
        print(f"✗ Pillow import failed: {e}")
        print("  Install with: pip install Pillow")
        return False
    
    # Optional imports
    try:
        import pillow_heif
        print("✓ pillow-heif available (HEIF/HEIC support)")
    except ImportError:
        print("○ pillow-heif not available (optional)")
    
    try:
        from reportlab.pdfgen import canvas
        print("✓ reportlab available (PDF support)")
    except ImportError:
        print("○ reportlab not available (optional)")
    
    try:
        from svglib.svglib import svg2rlg
        print("✓ svglib available (SVG support)")
    except ImportError:
        print("○ svglib not available (optional)")
    
    try:
        from psd_tools import PSDImage
        print("✓ psd-tools available (PSD support)")
    except ImportError:
        print("○ psd-tools not available (optional)")
    
    return True

def test_module_structure():
    """Test if the main module has correct structure"""
    print("\nTesting module structure...")
    
    try:
        # Mock tkinter if not available
        if 'tkinter' not in sys.modules:
            import types
            sys.modules['tkinter'] = types.ModuleType('tkinter')
            sys.modules['tkinter.filedialog'] = types.ModuleType('filedialog')
            sys.modules['tkinter.messagebox'] = types.ModuleType('messagebox')
            sys.modules['tkinter.ttk'] = types.ModuleType('ttk')
        
        import image_converter
        print("✓ image_converter module loaded")
        
        # Check for main class
        if hasattr(image_converter, 'ImageConverterApp'):
            print("✓ ImageConverterApp class found")
        else:
            print("✗ ImageConverterApp class not found")
            return False
        
        # Check for main function
        if hasattr(image_converter, 'main'):
            print("✓ main() function found")
        else:
            print("✗ main() function not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Module structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_class_methods():
    """Test if the ImageConverterApp class has required methods"""
    print("\nTesting class methods...")
    
    try:
        # Mock tkinter if not available
        if 'tkinter' not in sys.modules:
            import types
            sys.modules['tkinter'] = types.ModuleType('tkinter')
            sys.modules['tkinter.filedialog'] = types.ModuleType('filedialog')
            sys.modules['tkinter.messagebox'] = types.ModuleType('messagebox')
            sys.modules['tkinter.ttk'] = types.ModuleType('ttk')
        
        import image_converter
        app_class = image_converter.ImageConverterApp
        
        required_methods = [
            'setup_ui',
            'select_input_file',
            'select_output_file',
            'convert_image',
            'load_image',
            'save_image',
            'on_format_change',
            'toggle_resize'
        ]
        
        all_present = True
        for method_name in required_methods:
            if hasattr(app_class, method_name):
                print(f"✓ {method_name}() method found")
            else:
                print(f"✗ {method_name}() method not found")
                all_present = False
        
        return all_present
        
    except Exception as e:
        print(f"✗ Class methods test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_conversion():
    """Test basic image conversion (if PIL is available)"""
    print("\nTesting basic conversion functionality...")
    
    try:
        from PIL import Image
        import tempfile
        
        # Create a simple test image
        print("Creating test image...")
        test_img = Image.new('RGB', (100, 100), color='red')
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_input:
            input_path = tmp_input.name
            test_img.save(input_path, 'PNG')
            print(f"✓ Test image created: {input_path}")
        
        # Try to load it back
        loaded_img = Image.open(input_path)
        print(f"✓ Image loaded successfully: {loaded_img.size}, {loaded_img.mode}")
        
        # Try to save in different format
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_output:
            output_path = tmp_output.name
            loaded_img.save(output_path, 'JPEG', quality=85)
            print(f"✓ Image converted to JPEG: {output_path}")
        
        # Cleanup
        try:
            os.unlink(input_path)
            os.unlink(output_path)
            print("✓ Cleanup successful")
        except:
            pass
        
        return True
        
    except ImportError:
        print("○ Skipping conversion test (PIL not available)")
        return True
    except Exception as e:
        print(f"✗ Conversion test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Image Converter Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Import Test", test_imports()))
    results.append(("Module Structure Test", test_module_structure()))
    results.append(("Class Methods Test", test_class_methods()))
    results.append(("Basic Conversion Test", test_basic_conversion()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
