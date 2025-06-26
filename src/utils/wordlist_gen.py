#!/usr/bin/env python3
"""
Standalone wordlist generator for date-based passwords.
Uses crunch for efficient generation when available.
"""

import argparse
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.password_generator import CrunchPasswordGenerator, CrunchMultiFormatGenerator


def progress_callback(progress: float, current: int, total: int):
    """Progress callback for wordlist generation."""
    bar_length = 50
    filled_length = int(bar_length * progress / 100)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    print(f'\r|{bar}| {progress:.1f}% ({current}/{total})', end='', flush=True)


def main():
    parser = argparse.ArgumentParser(
        description='Generate wordlists for date-based passwords (DDMMYYYY format)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Generate passwords for 2020-2025:
    python wordlist_gen.py --start 2020 --end 2025 --output passwords.txt
  
  Generate multiple formats:
    python wordlist_gen.py --start 2020 --end 2025 --formats DDMMYYYY DDMMYY --output multi.txt
  
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
        '--formats',
        nargs='+',
        choices=['DDMMYYYY', 'DDMMYY', 'MMDDYYYY', 'MMDDYY', 'YYYYMMDD', 'YYMMDD'],
        default=['DDMMYYYY'],
        help='Date formats to generate (default: DDMMYYYY)'
    )
    
    parser.add_argument(
        '--estimate-only',
        action='store_true',
        help='Only show size estimate without generating'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    try:
        # Validate arguments
        if args.start > args.end:
            print("Error: Start year must be less than or equal to end year", file=sys.stderr)
            return 1
        
        # Choose generator based on formats
        if len(args.formats) == 1 and args.formats[0] == 'DDMMYYYY':
            generator = CrunchPasswordGenerator(args.start, args.end)
        else:
            generator = CrunchMultiFormatGenerator(args.start, args.end, args.formats)
        
        # Show information
        if len(args.formats) == 1:
            total_passwords = generator.count_valid_dates()
        else:
            total_passwords = generator.count_valid_dates() * len(args.formats)
        
        file_size = generator.get_file_size_estimate()
        if len(args.formats) > 1:
            file_size *= len(args.formats)
        
        print(f"Configuration:")
        print(f"  Year range: {args.start} - {args.end}")
        print(f"  Formats: {', '.join(args.formats)}")
        print(f"  Total passwords: {total_passwords:,}")
        print(f"  Estimated file size: {generator.format_file_size(file_size)}")
        
        if args.estimate_only:
            print("\nEstimate only - no file generated.")
            return 0
        
        # Check if output file exists
        if os.path.exists(args.output):
            response = input(f"\nFile '{args.output}' already exists. Overwrite? (y/N): ")
            if response.lower() not in ['y', 'yes']:
                print("Cancelled.")
                return 0
        
        # Create output directory if needed
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"\nGenerating wordlist to '{args.output}'...")
        
        # Generate wordlist
        if len(args.formats) == 1 and args.formats[0] == 'DDMMYYYY':
            generator.generate_wordlist_with_crunch(args.output, progress_callback if args.verbose else None)
        else:
            generator.generate_wordlist_multi_format(args.output, progress_callback if args.verbose else None)
        
        if args.verbose:
            print()  # New line after progress bar
        
        # Show final stats
        actual_size = os.path.getsize(args.output)
        print(f"\nWordlist generated successfully!")
        print(f"  File: {args.output}")
        print(f"  Size: {generator.format_file_size(actual_size)}")
        print(f"  Lines: {total_passwords:,}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\nCancelled by user.")
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())