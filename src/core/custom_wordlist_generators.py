#!/usr/bin/env python3
"""
Custom wordlist generators for specialized password patterns.
Handles date-based passwords, Buddhist calendar dates, and other patterns.
"""

from typing import Optional, Callable, Union
from pathlib import Path
from datetime import datetime, timedelta


class DateWordlistGenerator:
    """Generator for date-based password wordlists."""
    
    def generate_date_wordlist(
        self,
        output_path: Union[str, Path],
        start_year: int,
        end_year: int,
        date_format: str = "DDMMYYYY",
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> bool:
        """
        Generate date-based wordlist.
        
        Args:
            output_path: Output file path
            start_year: Starting year
            end_year: Ending year (inclusive)
            date_format: Date format (DDMMYYYY, DDMMYY, YYYYMMDD)
            progress_callback: Optional progress callback
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if progress_callback:
                progress_callback(0, f"Generating dates {start_year}-{end_year}")
            
            total_years = end_year - start_year + 1
            passwords_written = 0
            
            with open(output_path, 'w') as f:
                for year_offset, year in enumerate(range(start_year, end_year + 1)):
                    # Generate all valid dates for this year
                    current_date = datetime(year, 1, 1)
                    end_date = datetime(year, 12, 31)
                    
                    while current_date <= end_date:
                        if date_format == "DDMMYYYY":
                            password = f"{current_date.day:02d}{current_date.month:02d}{current_date.year:04d}"
                        elif date_format == "DDMMYY":
                            password = f"{current_date.day:02d}{current_date.month:02d}{current_date.year % 100:02d}"
                        elif date_format == "YYYYMMDD":
                            password = f"{current_date.year:04d}{current_date.month:02d}{current_date.day:02d}"
                        else:
                            return False
                        
                        f.write(password + '\n')
                        passwords_written += 1
                        current_date += timedelta(days=1)
                    
                    if progress_callback:
                        progress = ((year_offset + 1) / total_years) * 100
                        progress_callback(progress, f"Generated year {year}")
            
            if progress_callback:
                progress_callback(100, f"Date generation complete - {passwords_written:,} passwords")
            
            return True
            
        except Exception as e:
            if progress_callback:
                progress_callback(0, f"Error: {str(e)}")
            return False

    def generate_buddhist_dates(
        self,
        output_path: Union[str, Path],
        start_year: int,
        end_year: int,
        date_format: str = "DDMMYYYY",
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> bool:
        """
        Generate Buddhist calendar dates (Gregorian + 543 years).
        
        Args:
            output_path: Output file path
            start_year: Starting Gregorian year
            end_year: Ending Gregorian year (inclusive)
            date_format: Date format
            progress_callback: Optional progress callback
            
        Returns:
            True if successful, False otherwise
        """
        # Convert to Buddhist years (+543)
        buddhist_start = start_year + 543
        buddhist_end = end_year + 543
        
        if progress_callback:
            progress_callback(0, f"Generating Buddhist dates {buddhist_start}-{buddhist_end}")
        
        try:
            total_years = end_year - start_year + 1
            passwords_written = 0
            
            with open(output_path, 'w') as f:
                for year_offset, gregorian_year in enumerate(range(start_year, end_year + 1)):
                    buddhist_year = gregorian_year + 543
                    
                    # Generate all valid dates for this year
                    current_date = datetime(gregorian_year, 1, 1)
                    end_date = datetime(gregorian_year, 12, 31)
                    
                    while current_date <= end_date:
                        if date_format == "DDMMYYYY":
                            password = f"{current_date.day:02d}{current_date.month:02d}{buddhist_year:04d}"
                        elif date_format == "DDMMYY":
                            password = f"{current_date.day:02d}{current_date.month:02d}{buddhist_year % 100:02d}"
                        elif date_format == "YYYYMMDD":
                            password = f"{buddhist_year:04d}{current_date.month:02d}{current_date.day:02d}"
                        else:
                            return False
                        
                        f.write(password + '\n')
                        passwords_written += 1
                        current_date += timedelta(days=1)
                    
                    if progress_callback:
                        progress = ((year_offset + 1) / total_years) * 100
                        progress_callback(progress, f"Generated Buddhist year {buddhist_year}")
            
            if progress_callback:
                progress_callback(100, f"Buddhist date generation complete - {passwords_written:,} passwords")
            
            return True
            
        except Exception as e:
            if progress_callback:
                progress_callback(0, f"Error: {str(e)}")
            return False


class CustomWordlistGenerator:
    """Main class for custom wordlist generation patterns."""
    
    def __init__(self):
        self.date_generator = DateWordlistGenerator()
    
    def generate_date_wordlist(self, *args, **kwargs):
        """Generate date-based wordlist."""
        return self.date_generator.generate_date_wordlist(*args, **kwargs)
    
    def generate_buddhist_dates(self, *args, **kwargs):
        """Generate Buddhist calendar dates."""
        return self.date_generator.generate_buddhist_dates(*args, **kwargs)
    
    def calculate_date_count(self, start_year: int, end_year: int) -> int:
        """Calculate number of valid dates in range."""
        total_days = 0
        for year in range(start_year, end_year + 1):
            if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                total_days += 366  # Leap year
            else:
                total_days += 365
        return total_days