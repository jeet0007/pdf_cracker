#!/usr/bin/env python3
"""
Simple wordlist generator for date-based passwords.
Uses crunch wrapper for efficient generation.
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.crunch_wrapper import CrunchWrapper


def calculate_date_count(start_year: int, end_year: int) -> int:
    """Calculate number of valid dates in range."""
    total_days = 0
    for year in range(start_year, end_year + 1):
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            total_days += 366  # Leap year
        else:
            total_days += 365
    return total_days


def main():
    parser = argparse.ArgumentParser(
        description='Generate wordlists for date-based passwords',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Generate DDMMYYYY passwords for 2020-2025:
    python wordlist_gen.py --start 2020 --end 2025 --output passwords.txt
  
  Generate YYYYMMDD format:
    python wordlist_gen.py --start 2020 --end 2025 --format YYYYMMDD --output dates.txt
  
  Show size estimate without generating:
    python wordlist_gen.py --start 2020 --end 2025 --estimate-only
        """
    )
    
    parser.add_argument(
        '--start', '--start-year',
        type=int,
        default=2000,
        help='Start year (default: 2000)'
    )
    
    parser.add_argument(
        '--end', '--end-year',
        type=int,
        default=2030,
        help='End year (default: 2030)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='wordlists/dates_wordlist.txt',
        help='Output file path (default: wordlists/dates_wordlist.txt)'
    )
    
    parser.add_argument(
        '--format',
        choices=['DDMMYYYY', 'DDMMYY', 'YYYYMMDD'],
        default='DDMMYYYY',
        help='Date format (default: DDMMYYYY)'
    )
    
    parser.add_argument(
        '--estimate-only',
        action='store_true',
        help='Only show size estimate without generating'
    )
    
    args = parser.parse_args()
    
    try:
        # Validate arguments
        if args.start > args.end:
            print("Error: Start year must be less than or equal to end year", file=sys.stderr)
            return 1
        
        # Calculate estimates
        total_passwords = calculate_date_count(args.start, args.end)
        file_size_mb = (total_passwords * 9) / (1024 * 1024)  # ~9 bytes per line
        
        print(f"📊 Wordlist Configuration:")
        print(f"   📅 Year range: {args.start} - {args.end}")
        print(f"   📝 Format: {args.format}")
        print(f"   🔢 Total passwords: {total_passwords:,}")
        print(f"   📏 Estimated file size: {file_size_mb:.1f} MB")
        
        if args.estimate_only:
            print("\n✅ Estimate only - no file generated.")
            return 0
        
        # Check if output file exists
        if os.path.exists(args.output):
            response = input(f"\n⚠️  File '{args.output}' already exists. Overwrite? (y/N): ")
            if response.lower() not in ['y', 'yes']:
                print("❌ Cancelled.")
                return 0
        
        # Create output directory if needed
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"\n🚀 Generating wordlist to '{args.output}'...")
        
        # Initialize crunch wrapper
        crunch = CrunchWrapper()
        
        def progress_callback(progress: float, message: str):
            print(f"📊 {progress:.1f}% - {message}")
        
        # Generate wordlist
        success = crunch.generate_date_wordlist(
            args.output,
            args.start,
            args.end,
            args.format,
            progress_callback
        )
        
        if success:
            # Show final stats
            actual_size = os.path.getsize(args.output)
            actual_size_mb = actual_size / (1024 * 1024)
            
            print(f"\n🎉 Wordlist generated successfully!")
            print(f"   📄 File: {args.output}")
            print(f"   📏 Size: {actual_size_mb:.1f} MB")
            print(f"   📊 Lines: {total_passwords:,}")
            
            if not crunch.has_crunch:
                print(f"\n💡 Note: Used Python fallback (crunch not found)")
                print(f"   Install crunch for better performance: sudo apt install crunch")
            
            return 0
        else:
            print(f"\n❌ Failed to generate wordlist")
            return 1
        
    except KeyboardInterrupt:
        print("\n⏸️  Cancelled by user.")
        return 1
    except Exception as e:
        print(f"💥 Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())