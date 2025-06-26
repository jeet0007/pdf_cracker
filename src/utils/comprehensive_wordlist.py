#!/usr/bin/env python3
"""
CLI tool for generating comprehensive wordlist using the core modules.
"""

import sys
import os
from pathlib import Path
import argparse

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.password_generator import ComprehensivePasswordGenerator

def main():
    parser = argparse.ArgumentParser(
        description='Generate comprehensive PDF password wordlist',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This generates a comprehensive wordlist containing:
1. Gregorian calendar dates (past 80 years, multiple formats)
2. Buddhist calendar dates (past 80 years, multiple formats)  
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
    
    # Initialize generator
    generator = ComprehensivePasswordGenerator(years_back=args.years_back)
    
    # Show estimates
    stats = generator.estimate_size()
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
    
    # Generate wordlist
    try:
        print(f"\n🚀 Starting wordlist generation...")
        
        def progress_callback(progress, message):
            print(f"📊 {progress:.1f}% - {message}")
        
        result_path, total_written = generator.generate_comprehensive_wordlist(
            str(output_path), 
            progress_callback
        )
        
        # Final statistics
        actual_size = output_path.stat().st_size
        print(f"\n🎉 Comprehensive wordlist generated successfully!")
        print(f"📄 File: {result_path}")
        print(f"📊 Passwords: {total_written:,}")
        print(f"📏 Actual size: {actual_size / (1024 * 1024):.1f} MB")
        print(f"\n🔍 You can now use this wordlist with:")
        print(f"   python src/utils/comprehensive_crack.py")
        
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