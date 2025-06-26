#!/usr/bin/env python3
"""
Quick installation test for PDF Cracker.
"""

import sys
import os
import subprocess
import shutil
from pathlib import Path

def test_python_version():
    """Test Python version."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 7:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need 3.7+")
        return False

def test_john_the_ripper():
    """Test John the Ripper installation."""
    if shutil.which('john'):
        try:
            result = subprocess.run(['john', '--version'], capture_output=True, text=True)
            print(f"✅ John the Ripper - OK")
            return True
        except:
            print("❌ John the Ripper - Found but not working")
            return False
    else:
        print("❌ John the Ripper - Not found")
        return False

def test_crunch():
    """Test crunch installation."""
    if shutil.which('crunch'):
        print("✅ Crunch - OK")
        return True
    else:
        print("⚠️  Crunch - Not found (optional)")
        return True

def test_pdf2john():
    """Test pdf2john availability."""
    paths = [
        '/usr/share/john/pdf2john.pl',
        '/opt/homebrew/share/john/pdf2john.pl',
        '/usr/local/share/john/pdf2john.pl'
    ]
    
    import glob
    glob_paths = glob.glob('/opt/homebrew/Cellar/john-jumbo/*/share/john/pdf2john.pl')
    paths.extend(glob_paths)
    
    for path in paths:
        if Path(path).exists():
            print(f"✅ pdf2john found at {path}")
            return True
    
    print("❌ pdf2john.pl - Not found")
    return False

def test_imports():
    """Test Python imports."""
    success = True
    
    # Test core imports
    try:
        import tkinter
        print("✅ tkinter - OK")
    except ImportError:
        print("❌ tkinter - Not available")
        success = False
    
    # Test optional imports
    try:
        import tkinterdnd2
        print("✅ tkinterdnd2 - OK")
    except ImportError:
        print("⚠️  tkinterdnd2 - Not found (drag-drop disabled)")
    
    return success

def test_modules():
    """Test our modules can be imported."""
    sys.path.insert(0, 'src')
    
    try:
        from core.password_generator import CrunchPasswordGenerator
        print("✅ Password generator module - OK")
    except ImportError as e:
        print(f"❌ Password generator module - {e}")
        return False
    
    try:
        from core.pdf_processor import PDFProcessor
        print("✅ PDF processor module - OK")
    except ImportError as e:
        print(f"❌ PDF processor module - {e}")
        return False
    
    try:
        from core.cracker import PDFCracker
        print("✅ PDF cracker module - OK")
    except ImportError as e:
        print(f"❌ PDF cracker module - {e}")
        return False
    
    return True

def test_wordlist_generator():
    """Test wordlist generation."""
    sys.path.insert(0, 'src')
    
    try:
        from core.password_generator import CrunchPasswordGenerator
        gen = CrunchPasswordGenerator(2024, 2024)
        count = gen.count_valid_dates()
        
        if count == 366:  # 2024 is a leap year
            print(f"✅ Wordlist generation - OK ({count} passwords for 2024)")
            return True
        else:
            print(f"❌ Wordlist generation - Wrong count: {count}")
            return False
    except Exception as e:
        print(f"❌ Wordlist generation - {e}")
        return False

def main():
    """Run all tests."""
    print("🔐 PDF Cracker Installation Test")
    print("================================")
    print()
    
    tests = [
        ("Python Version", test_python_version),
        ("John the Ripper", test_john_the_ripper),
        ("Crunch", test_crunch),
        ("pdf2john", test_pdf2john),
        ("Python Imports", test_imports),
        ("Module Imports", test_modules),
        ("Wordlist Generation", test_wordlist_generator),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"Testing {name}...")
        if test_func():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Installation looks good.")
        print("\nYou can now run:")
        print("  GUI:       python src/main.py")
        print("  Wordlist:  python src/wordlist_gen.py --help")
    else:
        print("⚠️  Some tests failed. Check the installation.")
        print("\nTry running the installation script:")
        print("  Linux/macOS: ./install.sh")
        print("  Windows:     install.bat")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)