#!/usr/bin/env python3
"""
CLI tool for generating comprehensive wordlist using core wrappers.
Combines dates and 8-digit numbers into one massive wordlist.
"""

import sys
import os
from pathlib import Path
import argparse
import tempfile

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.crunch_wrapper import CrunchWrapper


def calculate_comprehensive_stats(years_back: int):
    """Calculate comprehensive wordlist statistics."""
    from datetime import datetime
    
    current_year = datetime.now().year
    start_year = current_year - years_back
    
    # Calculate Gregorian dates
    gregorian_days = 0
    for year in range(start_year, current_year + 1):
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            gregorian_days += 366
        else:
            gregorian_days += 365
    
    # Calculate Buddhist dates (same count, +543 years)
    buddhist_days = gregorian_days
    
    # 8-digit numbers: 00000000 to 99999999
    eight_digit_numbers = 100000000
    
    total_passwords = gregorian_days + buddhist_days + eight_digit_numbers
    file_size_mb = (total_passwords * 9) / (1024 * 1024)  # ~9 bytes per line
    
    return {
        'gregorian_dates': gregorian_days,
        'buddhist_dates': buddhist_days,
        'numbers': eight_digit_numbers,
        'total_passwords': total_passwords,
        'file_size_mb': file_size_mb
    }


def main():
    parser = argparse.ArgumentParser(
        description='Generate comprehensive PDF password wordlist',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This generates a comprehensive wordlist containing:
1. Gregorian calendar dates (past 80 years, DDMMYYYY format)
2. Buddhist calendar dates (past 80 years, DDMMYYYY format)  
3. All 8-digit numbers (00000000 to 99999999)

WARNING: This creates a very large file (~900MB with 100M+ passwords)

Examples:
  python src/utils/comprehensive_wordlist.py
  python src/utils/comprehensive_wordlist.py --output wordlists/ultimate.txt
  python src/utils/comprehensive_wordlist.py --years-back 50 --estimate-only
        """
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='wordlists/comprehensive_ultimate.txt',
        help='Output wordlist file (default: wordlists/comprehensive_ultimate.txt)'
    )
    
    parser.add_argument(
        '--years-back',
        type=int,
        default=80,
        help='How many years back to generate dates (default: 80)'
    )
    
    parser.add_argument(
        '--estimate-only',
        action='store_true',
        help='Only show size estimate without generating'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Skip confirmation prompt'
    )
    
    args = parser.parse_args()
    
    print("🎯 Comprehensive PDF Password Wordlist Generator")
    print("================================================")
    
    # Calculate estimates
    stats = calculate_comprehensive_stats(args.years_back)
    
    print(f"📊 Estimated wordlist statistics:")
    print(f"   📅 Gregorian dates: {stats['gregorian_dates']:,}")
    print(f"   🧘 Buddhist dates: {stats['buddhist_dates']:,}")
    print(f"   🔢 8-digit numbers: {stats['numbers']:,}")
    print(f"   📝 Total passwords: {stats['total_passwords']:,}")
    print(f"   📏 File size: {stats['file_size_mb']:.1f} MB")
    print(f"   🗂️  Output: {args.output}")
    
    if args.estimate_only:
        print("\n✅ Estimate complete (no file generated)")
        return 0
    
    # Confirm generation
    if not args.force:
        print(f"\n⚠️  WARNING: This will create a {stats['file_size_mb']:.1f} MB file!")
        print(f"⏱️  Generation may take 15-30 minutes")
        try:
            confirm = input("\nProceed? (y/N): ").lower().strip()
            if confirm not in ['y', 'yes']:
                print("❌ Cancelled")
                return 0
        except KeyboardInterrupt:
            print("\n❌ Cancelled")
            return 0
    
    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Generate comprehensive wordlist
    try:
        print(f"\n🚀 Starting comprehensive wordlist generation...")
        
        crunch = CrunchWrapper()
        total_written = 0
        
        def progress_callback(progress: float, message: str):
            print(f"📊 {progress:.1f}% - {message}")
        
        # Generate in parts and combine
        with open(output_path, 'w') as final_file:
            # 1. Gregorian dates
            print("📅 Generating Gregorian dates...")
            with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
                temp_path = temp_file.name
            
            from datetime import datetime
            current_year = datetime.now().year
            start_year = current_year - args.years_back
            
            success = crunch.generate_date_wordlist(
                temp_path,
                start_year,
                current_year,
                "DDMMYYYY",
                progress_callback
            )
            
            if success:
                with open(temp_path, 'r') as temp_file:
                    for line in temp_file:
                        final_file.write(line)
                        total_written += 1
                os.unlink(temp_path)
            else:
                print("❌ Failed to generate Gregorian dates")
                return 1
            
            # 2. Buddhist dates (Gregorian + 543 years)
            print("🧘 Generating Buddhist dates...")
            with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
                temp_path = temp_file.name
            
            success = crunch.generate_date_wordlist(
                temp_path,
                start_year + 543,  # Buddhist years
                current_year + 543,
                "DDMMYYYY",
                progress_callback
            )
            
            if success:
                with open(temp_path, 'r') as temp_file:
                    for line in temp_file:
                        final_file.write(line)
                        total_written += 1
                os.unlink(temp_path)
            else:
                print("❌ Failed to generate Buddhist dates")
                return 1
            
            # 3. All 8-digit numbers
            print("🔢 Generating 8-digit numbers...")
            with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
                temp_path = temp_file.name
            
            success = crunch.generate_number_range(
                temp_path,
                0,
                99999999,
                8,
                progress_callback
            )
            
            if success:
                with open(temp_path, 'r') as temp_file:
                    for line in temp_file:
                        final_file.write(line)
                        total_written += 1
                os.unlink(temp_path)
            else:
                print("❌ Failed to generate 8-digit numbers")
                return 1
        
        # Final statistics
        actual_size = output_path.stat().st_size
        print(f"\n🎉 Comprehensive wordlist generated successfully!")
        print(f"📄 File: {output_path}")
        print(f"📊 Passwords: {total_written:,}")
        print(f"📏 Actual size: {actual_size / (1024 * 1024):.1f} MB")
        print(f"\n🔍 You can now use this wordlist with:")
        print(f"   python src/utils/comprehensive_crack.py")
        
        if not crunch.has_crunch:
            print(f"\n💡 Note: Used Python fallback (crunch not found)")
            print(f"   Install crunch for better performance: sudo apt install crunch")
        
        return 0
        
    except KeyboardInterrupt:
        print(f"\n⏸️  Generation interrupted")
        if output_path.exists():
            print(f"🗑️  Cleaning up partial file...")
            output_path.unlink()
        return 1
    except Exception as e:
        print(f"💥 Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())