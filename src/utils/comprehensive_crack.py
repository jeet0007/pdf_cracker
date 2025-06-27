#!/usr/bin/env python3
"""
CLI tool for cracking PDFs using the comprehensive wordlist.
"""

import sys
import os
from pathlib import Path
import argparse
import subprocess
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.john_wrapper import PDFCracker, CrackResult

def analyze_password(password: str):
    """Analyze what type of password was found."""
    print(f"\n🔍 Password Analysis:")
    print(f"   🔑 Password: '{password}'")
    print(f"   📏 Length: {len(password)} characters")
    
    if password.isdigit() and len(password) == 8:
        print(f"   🔢 Type: 8-digit number")
        
        # Try to parse as different date formats
        if password.startswith(('19', '20')):
            # YYYYMMDD format
            year = password[:4]
            month = password[4:6]
            day = password[6:8]
            print(f"   📅 Possible YYYYMMDD: {day}/{month}/{year}")
        
        elif password.startswith(('25', '26')):
            # Possible Buddhist YYYYMMDD
            year = int(password[:4])
            month = password[4:6] 
            day = password[6:8]
            gregorian_year = year - 543
            if 1900 <= gregorian_year <= 2100:
                print(f"   🧘 Possible Buddhist YYYYMMDD: {day}/{month}/{year} (Buddhist) = {day}/{month}/{gregorian_year} (Gregorian)")
        
        else:
            # DDMMYYYY format
            day = password[:2]
            month = password[2:4]
            year = password[4:8]
            
            if 1900 <= int(year) <= 2100:
                print(f"   📅 Possible DDMMYYYY: {day}/{month}/{year}")
            elif 2400 <= int(year) <= 2700:
                # Buddhist year
                buddhist_year = int(year)
                gregorian_year = buddhist_year - 543
                print(f"   🧘 Possible Buddhist DDMMYYYY: {day}/{month}/{year} (Buddhist) = {day}/{month}/{gregorian_year} (Gregorian)")
    else:
        print(f"   🔤 Type: Non-numeric or different length")

def check_wordlist_exists(wordlist_path: Path) -> bool:
    """Check if comprehensive wordlist exists and get stats."""
    if not wordlist_path.exists():
        print(f"❌ Comprehensive wordlist not found: {wordlist_path}")
        print(f"📝 Please generate it first:")
        print(f"   python src/utils/comprehensive_wordlist.py")
        return False
    
    # Get wordlist stats
    size = wordlist_path.stat().st_size
    size_mb = size / (1024 * 1024)
    
    print(f"✅ Comprehensive wordlist found:")
    print(f"   📄 File: {wordlist_path}")
    print(f"   📏 Size: {size_mb:.1f} MB")
    
    # Quick line count for smaller files, estimate for larger ones
    if size_mb < 100:
        print(f"   📊 Counting passwords...")
        try:
            result = subprocess.run(['wc', '-l', str(wordlist_path)], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                line_count = int(result.stdout.split()[0])
                print(f"   🔢 Passwords: {line_count:,}")
            else:
                print(f"   🔢 Passwords: ~{int(size / 9):,} (estimated)")
        except:
            print(f"   🔢 Passwords: ~{int(size / 9):,} (estimated)")
    else:
        print(f"   🔢 Passwords: ~{int(size / 9):,} (estimated)")
    
    return True

def main():
    parser = argparse.ArgumentParser(
        description='Crack PDF using comprehensive wordlist',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This tool uses the comprehensive wordlist containing:
- Gregorian calendar dates (past 80 years)
- Buddhist calendar dates (past 80 years)
- All 8-digit numbers (00000000-99999999)

Examples:
  python src/utils/comprehensive_crack.py assets/document.pdf
  python src/utils/comprehensive_crack.py --wordlist custom.txt document.pdf
  python src/utils/comprehensive_crack.py --timeout 7200 document.pdf  # 2 hour timeout
        """
    )
    
    parser.add_argument(
        'pdf_path',
        help='Path to the PDF file to crack'
    )
    
    parser.add_argument(
        '--wordlist',
        type=str,
        default='wordlists/comprehensive_ultimate.txt',
        help='Path to wordlist file (default: wordlists/comprehensive_ultimate.txt)'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=3600,
        help='Timeout in seconds (default: 3600 = 1 hour)'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Skip confirmation prompt'
    )
    
    args = parser.parse_args()
    
    print("🔨 Comprehensive PDF Password Cracker")
    print("====================================")
    
    # Check if PDF exists
    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        print(f"❌ PDF not found: {pdf_path}")
        return 1
    
    print(f"📄 Target PDF: {pdf_path}")
    
    # Check if wordlist exists
    wordlist_path = Path(args.wordlist)
    if not check_wordlist_exists(wordlist_path):
        return 1
    
    # Initialize cracker and check PDF
    cracker = PDFCracker()
    pdf_info = cracker.get_pdf_info(pdf_path)
    
    if not pdf_info.get('protected', False):
        print(f"✅ PDF is not password protected")
        print(f"📂 File: {pdf_path}")
        print(f"📏 Size: {pdf_info['size']:,} bytes")
        print(f"\n🎉 No password needed! You can open this PDF directly.")
        return 0
    
    print(f"✅ PDF is password protected")
    print(f"📏 PDF size: {pdf_info['size']:,} bytes")
    
    # Estimate cracking time
    wordlist_size_mb = wordlist_path.stat().st_size / (1024 * 1024)
    estimated_minutes = max(1, int(wordlist_size_mb / 10))  # Rough estimate
    
    print(f"\n⚠️  Cracking Information:")
    print(f"   ⏱️  Estimated time: {estimated_minutes//60}h {estimated_minutes%60}m (very rough estimate)")
    print(f"   🔄 Timeout: {args.timeout//60} minutes")
    print(f"   💾 This may use significant CPU and memory")
    print(f"   ⏹️  Press Ctrl+C to stop if needed")
    
    if not args.force:
        try:
            confirm = input(f"\n🚀 Start cracking? (y/N): ").lower().strip()
            if confirm not in ['y', 'yes']:
                print("❌ Cancelled")
                return 0
        except KeyboardInterrupt:
            print("\n❌ Cancelled")
            return 0
    
    # Start cracking
    print(f"\n🔨 Starting PDF crack attempt...")
    print(f"⏳ This may take a very long time...")
    
    start_time = time.time()
    
    def progress_callback(progress: float, attempts: int):
        if attempts % 10000 == 0:  # Update every 10k attempts
            elapsed = time.time() - start_time
            print(f"📊 Progress: {progress:.1f}% | Attempts: {attempts:,} | Elapsed: {elapsed/60:.1f}m")
    
    try:
        result = cracker.crack_pdf(
            pdf_path,
            wordlist_path,
            progress_callback
        )
        
        elapsed_time = time.time() - start_time
        
        if result.success:
            print(f"\n🎉 SUCCESS! Password found!")
            print(f"🔑 Password: '{result.password}'")
            print(f"⏱️  Time taken: {elapsed_time/60:.1f} minutes ({elapsed_time:.1f} seconds)")
            
            # Analyze the password
            analyze_password(result.password)
            
            print(f"\n💾 You can now open the PDF with this password")
            return 0
        else:
            print(f"\n❌ Password not found")
            print(f"⏱️  Time taken: {elapsed_time/60:.1f} minutes")
            if result.error:
                print(f"💥 Error: {result.error}")
            print(f"\n🤔 The password might not be in our wordlist:")
            print(f"   - Not a date or 8-digit number")
            print(f"   - Uses letters/symbols")
            print(f"   - Different calendar system")
            print(f"   - Longer than 8 characters")
            return 1
            
    except KeyboardInterrupt:
        elapsed_time = time.time() - start_time
        print(f"\n⏸️  Cracking interrupted after {elapsed_time/60:.1f} minutes")
        print(f"🔄 You can resume with: john --restore")
        return 1
    except Exception as e:
        print(f"💥 Cracking error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())