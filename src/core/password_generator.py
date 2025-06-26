#!/usr/bin/env python3

import subprocess
import os
import tempfile
import calendar
from datetime import datetime
from typing import List, Optional, Callable
import shutil


class CrunchPasswordGenerator:
    """Generate DDMMYYYY passwords using crunch tool."""
    
    def __init__(self, start_year: int = 2000, end_year: int = 2030):
        self.start_year = start_year
        self.end_year = end_year
        self.validate_years()
        self.check_crunch_available()
    
    def validate_years(self):
        """Validate year range."""
        if self.start_year > self.end_year:
            raise ValueError("Start year must be less than or equal to end year")
        if self.start_year < 1900 or self.end_year > 2100:
            raise ValueError("Years must be between 1900 and 2100")
    
    def check_crunch_available(self):
        """Check if crunch is available on the system."""
        if not shutil.which('crunch'):
            raise RuntimeError("crunch is not installed. Please install it using your package manager.")
    
    def generate_date_patterns(self) -> List[str]:
        """Generate crunch patterns for DDMMYYYY format."""
        patterns = []
        
        for year in range(self.start_year, self.end_year + 1):
            for month in range(1, 13):
                days_in_month = calendar.monthrange(year, month)[1]
                
                # Create pattern for each month
                day_pattern = "01" if days_in_month >= 1 else ""
                if days_in_month >= 10:
                    day_pattern = "[01][0-9]"
                if days_in_month >= 20:
                    day_pattern = "[0-2][0-9]"
                if days_in_month >= 30:
                    day_pattern = "[0-3][0-9]"
                
                # Adjust for actual days in month
                if days_in_month == 28:
                    day_pattern = "[0-2][0-8]"
                elif days_in_month == 29:
                    day_pattern = "[0-2][0-9]"
                elif days_in_month == 30:
                    day_pattern = "[0-3][0-9]"
                elif days_in_month == 31:
                    day_pattern = "[0-3][0-9]"
                
                month_str = f"{month:02d}"
                year_str = str(year)
                
                # For each day range, create specific patterns
                for day in range(1, days_in_month + 1):
                    patterns.append(f"{day:02d}{month_str}{year_str}")
        
        return patterns
    
    def generate_wordlist_with_crunch(self, output_path: str, progress_callback: Optional[Callable] = None):
        """
        Generate wordlist using crunch with DDMMYYYY pattern.
        
        Args:
            output_path: Output file path
            progress_callback: Optional callback for progress updates
        """
        # For DDMMYYYY format, we'll use a more direct approach
        # Generate patterns for valid dates only
        
        with open(output_path, 'w') as f:
            total_dates = self.count_valid_dates()
            current_count = 0
            
            for year in range(self.start_year, self.end_year + 1):
                for month in range(1, 13):
                    days_in_month = calendar.monthrange(year, month)[1]
                    
                    for day in range(1, days_in_month + 1):
                        if self.is_valid_date(day, month, year):
                            password = f"{day:02d}{month:02d}{year}"
                            f.write(password + '\n')
                            current_count += 1
                            
                            if progress_callback and current_count % 1000 == 0:
                                progress = (current_count / total_dates) * 100
                                progress_callback(progress, current_count, total_dates)
            
            if progress_callback:
                progress_callback(100, total_dates, total_dates)
        
        return output_path
    
    def generate_wordlist_with_crunch_pattern(self, output_path: str, pattern: str = None):
        """
        Generate wordlist using crunch with custom pattern.
        
        Args:
            output_path: Output file path
            pattern: Custom crunch pattern (default: optimized for date range)
        """
        if pattern is None:
            # Use a broad pattern and filter later
            pattern = "[0-3][0-9][0-1][0-9]" + "".join([str(y) for y in range(self.start_year, min(self.start_year + 10, self.end_year + 1))])
        
        cmd = ['crunch', '8', '8', '-t', pattern, '-o', output_path]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return output_path
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"crunch failed: {e.stderr}")
    
    def is_valid_date(self, day: int, month: int, year: int) -> bool:
        """Check if a date is valid."""
        try:
            datetime(year, month, day)
            return True
        except ValueError:
            return False
    
    def count_valid_dates(self) -> int:
        """Count total valid dates in the range."""
        count = 0
        for year in range(self.start_year, self.end_year + 1):
            for month in range(1, 13):
                days_in_month = calendar.monthrange(year, month)[1]
                count += days_in_month
        return count
    
    def get_file_size_estimate(self) -> int:
        """Estimate output file size in bytes."""
        date_count = self.count_valid_dates()
        bytes_per_password = 9  # 8 chars + newline
        return date_count * bytes_per_password
    
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"


class ComprehensivePasswordGenerator:
    """Generate comprehensive wordlist with dates, Buddhist dates, and all 8-digit numbers."""
    
    def __init__(self, years_back: int = 80):
        from datetime import date
        current_year = date.today().year
        self.start_year = current_year - years_back
        self.end_year = current_year + 5
        self.date_formats = ['DDMMYYYY', 'DDMMYY', 'MMDDYYYY', 'YYYYMMDD']
    
    def generate_comprehensive_wordlist(self, output_path: str, progress_callback: Optional[Callable] = None):
        """Generate comprehensive wordlist with all password types."""
        print(f"🎯 Generating comprehensive wordlist...")
        print(f"📅 Date range: {self.start_year} - {self.end_year}")
        print(f"📋 Includes: Gregorian dates, Buddhist dates, all 8-digit numbers")
        
        with open(output_path, 'w') as f:
            total_written = 0
            
            # 1. Gregorian dates
            if progress_callback:
                progress_callback(10, "Generating Gregorian dates...")
            
            gregorian_passwords = self._generate_date_passwords(False)
            for password in sorted(gregorian_passwords):
                f.write(password + '\n')
                total_written += 1
            
            print(f"✅ Written {len(gregorian_passwords):,} Gregorian passwords")
            
            # 2. Buddhist dates
            if progress_callback:
                progress_callback(30, "Generating Buddhist dates...")
            
            buddhist_passwords = self._generate_date_passwords(True)
            # Only add unique Buddhist passwords
            new_buddhist = buddhist_passwords - gregorian_passwords
            for password in sorted(new_buddhist):
                f.write(password + '\n')
                total_written += len(new_buddhist)
            
            print(f"✅ Written {len(new_buddhist):,} unique Buddhist passwords")
            
            # 3. All 8-digit numbers
            if progress_callback:
                progress_callback(50, "Generating 8-digit numbers...")
            
            print(f"🔢 Writing all 8-digit numbers (this will take time)...")
            existing_passwords = gregorian_passwords | buddhist_passwords
            number_count = 0
            
            for i in range(100000000):  # 0 to 99,999,999
                number = f"{i:08d}"
                if number not in existing_passwords:
                    f.write(number + '\n')
                    number_count += 1
                
                # Progress every million
                if (i + 1) % 1000000 == 0:
                    progress_pct = 50 + ((i + 1) / 100000000) * 40  # 50% to 90%
                    if progress_callback:
                        progress_callback(progress_pct, f"Numbers: {i+1:,}/100M")
                    print(f"  📊 {i+1:,}/100,000,000 ({((i+1)/100000000)*100:.1f}%)")
            
            total_written += number_count
            print(f"✅ Written {number_count:,} unique 8-digit numbers")
            
            if progress_callback:
                progress_callback(100, "Complete!")
        
        return output_path, total_written
    
    def _generate_date_passwords(self, buddhist: bool = False) -> set:
        """Generate date passwords (Gregorian or Buddhist)."""
        passwords = set()
        
        for year in range(self.start_year, self.end_year + 1):
            actual_year = year + 543 if buddhist else year
            
            for month in range(1, 13):
                days_in_month = calendar.monthrange(year, month)[1]
                
                for day in range(1, days_in_month + 1):
                    if self._is_valid_date(day, month, year):
                        for fmt in self.date_formats:
                            if fmt == 'DDMMYYYY':
                                password = f"{day:02d}{month:02d}{actual_year}"
                            elif fmt == 'DDMMYY':
                                password = f"{day:02d}{month:02d}{actual_year % 100:02d}"
                            elif fmt == 'MMDDYYYY':
                                password = f"{month:02d}{day:02d}{actual_year}"
                            elif fmt == 'YYYYMMDD':
                                password = f"{actual_year}{month:02d}{day:02d}"
                            
                            passwords.add(password)
        
        return passwords
    
    def _is_valid_date(self, day: int, month: int, year: int) -> bool:
        """Check if date is valid."""
        try:
            datetime(year, month, day)
            return True
        except ValueError:
            return False
    
    def estimate_size(self) -> dict:
        """Estimate wordlist statistics."""
        years = self.end_year - self.start_year + 1
        approx_days_per_year = 365.25
        dates_per_format = int(years * approx_days_per_year)
        
        gregorian_count = dates_per_format * len(self.date_formats)
        buddhist_count = dates_per_format * len(self.date_formats) 
        numbers_count = 100000000  # All 8-digit numbers
        
        # Estimate overlap (many Buddhist dates will be different from Gregorian)
        unique_dates = gregorian_count + int(buddhist_count * 0.8)  # Assume 80% unique
        total_passwords = unique_dates + numbers_count
        
        # File size estimate (9 bytes per password: 8 digits + newline)
        file_size_bytes = total_passwords * 9
        
        return {
            'gregorian_dates': gregorian_count,
            'buddhist_dates': buddhist_count,
            'numbers': numbers_count,
            'total_passwords': total_passwords,
            'file_size_bytes': file_size_bytes,
            'file_size_mb': file_size_bytes / (1024 * 1024)
        }


class CrunchMultiFormatGenerator(CrunchPasswordGenerator):
    """Generate multiple date formats using crunch."""
    
    FORMATS = {
        'DDMMYYYY': (8, 8, '[0-3][0-9][0-1][0-9]%%%%'),
        'DDMMYY': (6, 6, '[0-3][0-9][0-1][0-9]%%'),
        'MMDDYYYY': (8, 8, '[0-1][0-9][0-3][0-9]%%%%'),
        'MMDDYY': (6, 6, '[0-1][0-9][0-3][0-9]%%'),
        'YYYYMMDD': (8, 8, '%%%%[0-1][0-9][0-3][0-9]'),
        'YYMMDD': (6, 6, '%%[0-1][0-9][0-3][0-9]'),
    }
    
    def __init__(self, start_year: int = 2000, end_year: int = 2030, formats: List[str] = None):
        super().__init__(start_year, end_year)
        self.formats = formats or ['DDMMYYYY']
        self.validate_formats()
    
    def validate_formats(self):
        """Validate format strings."""
        for fmt in self.formats:
            if fmt not in self.FORMATS:
                raise ValueError(f"Unknown format: {fmt}. Available: {list(self.FORMATS.keys())}")
    
    def generate_wordlist_multi_format(self, output_path: str, progress_callback: Optional[Callable] = None):
        """Generate wordlist with multiple formats."""
        temp_files = []
        
        try:
            # Generate wordlist for each format
            for i, fmt in enumerate(self.formats):
                temp_file = tempfile.mktemp(suffix=f'_{fmt}.txt')
                temp_files.append(temp_file)
                
                if fmt == 'DDMMYYYY':
                    self.generate_wordlist_with_crunch(temp_file)
                else:
                    # For other formats, generate using the custom method
                    self._generate_format_wordlist(temp_file, fmt)
                
                if progress_callback:
                    progress = ((i + 1) / len(self.formats)) * 100
                    progress_callback(progress, i + 1, len(self.formats))
            
            # Combine all temporary files
            with open(output_path, 'w') as outfile:
                for temp_file in temp_files:
                    with open(temp_file, 'r') as infile:
                        outfile.write(infile.read())
        
        finally:
            # Clean up temporary files
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
        
        return output_path
    
    def _generate_format_wordlist(self, output_path: str, fmt: str):
        """Generate wordlist for specific format."""
        with open(output_path, 'w') as f:
            for year in range(self.start_year, self.end_year + 1):
                for month in range(1, 13):
                    days_in_month = calendar.monthrange(year, month)[1]
                    
                    for day in range(1, days_in_month + 1):
                        if self.is_valid_date(day, month, year):
                            if fmt == 'DDMMYY':
                                password = f"{day:02d}{month:02d}{year % 100:02d}"
                            elif fmt == 'MMDDYYYY':
                                password = f"{month:02d}{day:02d}{year}"
                            elif fmt == 'MMDDYY':
                                password = f"{month:02d}{day:02d}{year % 100:02d}"
                            elif fmt == 'YYYYMMDD':
                                password = f"{year}{month:02d}{day:02d}"
                            elif fmt == 'YYMMDD':
                                password = f"{year % 100:02d}{month:02d}{day:02d}"
                            else:
                                password = f"{day:02d}{month:02d}{year}"
                            
                            f.write(password + '\n')