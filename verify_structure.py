#!/usr/bin/env python3
"""
Structure verification script for image converter
Verifies the code structure without requiring all dependencies
"""

import ast
import sys

def verify_syntax():
    """Verify Python syntax"""
    print("Checking Python syntax...")
    try:
        with open('image_converter.py', 'r') as f:
            code = f.read()
        ast.parse(code)
        print("✓ Python syntax is valid")
        return True
    except SyntaxError as e:
        print(f"✗ Syntax error: {e}")
        return False

def verify_structure():
    """Verify code structure using AST"""
    print("\nChecking code structure...")

    try:
        with open('image_converter.py', 'r') as f:
            code = f.read()

        tree = ast.parse(code)

        # Find classes and functions
        classes = []
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
                # Get methods
                methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                print(f"✓ Found class: {node.name} with {len(methods)} methods")
            elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                functions.append(node.name)

        print(f"✓ Found {len(classes)} class(es)")
        print(f"✓ Found {len(functions)} top-level function(s)")

        # Check for required elements
        if 'ImageConverterApp' not in classes:
            print("✗ ImageConverterApp class not found")
            return False

        if 'main' not in functions:
            print("✗ main() function not found")
            return False

        print("✓ All required structural elements present")
        return True

    except Exception as e:
        print(f"✗ Structure check failed: {e}")
        return False

def check_imports():
    """Check what imports are used"""
    print("\nChecking imports...")

    try:
        with open('image_converter.py', 'r') as f:
            code = f.read()

        tree = ast.parse(code)

        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                imports.append(f"{node.module}")

        required_imports = ['tkinter', 'PIL']
        optional_imports = ['pillow_heif', 'reportlab', 'svglib', 'psd_tools']

        print("Required imports:")
        for imp in required_imports:
            if any(imp in i for i in imports):
                print(f"  ✓ {imp}")
            else:
                print(f"  ✗ {imp} (missing)")

        print("Optional imports (with fallback):")
        for imp in optional_imports:
            if any(imp in i for i in imports):
                print(f"  ✓ {imp}")

        return True

    except Exception as e:
        print(f"✗ Import check failed: {e}")
        return False

def check_files():
    """Check if required files exist"""
    print("\nChecking required files...")

    import os

    required_files = [
        'image_converter.py',
        'requirements.txt',
        'README.md'
    ]

    all_exist = True
    for filename in required_files:
        if os.path.exists(filename):
            print(f"✓ {filename} exists")
        else:
            print(f"✗ {filename} missing")
            all_exist = False

    optional_files = [
        'setup_venv.sh',
        'setup_venv.bat',
        'USAGE.md'
    ]

    print("Optional files:")
    for filename in optional_files:
        if os.path.exists(filename):
            print(f"  ✓ {filename}")
        else:
            print(f"  ○ {filename} (not found)")

    return all_exist

def main():
    """Run all verifications"""
    print("=" * 60)
    print("Image Converter Structure Verification")
    print("=" * 60)

    results = []
    results.append(("Syntax Check", verify_syntax()))
    results.append(("Structure Check", verify_structure()))
    results.append(("Import Check", check_imports()))
    results.append(("File Check", check_files()))

    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)

    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"\n{passed}/{total} checks passed")

    if passed == total:
        print("\n✓ All structural checks passed!")
        print("\nNote: To fully test functionality, install dependencies:")
        print("  pip install -r requirements.txt")
        return 0
    else:
        print("\n✗ Some checks failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
