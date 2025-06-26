#!/usr/bin/env python3
"""
Tests for password generator module.
"""

import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.password_generator import CrunchPasswordGenerator, CrunchMultiFormatGenerator


class TestCrunchPasswordGenerator(unittest.TestCase):
    """Test the CrunchPasswordGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = CrunchPasswordGenerator(2023, 2023)  # Single year for fast tests
    
    def test_init_valid_years(self):
        """Test initialization with valid years."""
        gen = CrunchPasswordGenerator(2020, 2025)
        self.assertEqual(gen.start_year, 2020)
        self.assertEqual(gen.end_year, 2025)
    
    def test_init_invalid_years(self):
        """Test initialization with invalid years."""
        with self.assertRaises(ValueError):
            CrunchPasswordGenerator(2025, 2020)  # Start > End
        
        with self.assertRaises(ValueError):
            CrunchPasswordGenerator(1800, 2020)  # Too early
        
        with self.assertRaises(ValueError):
            CrunchPasswordGenerator(2020, 2200)  # Too late
    
    def test_validate_years(self):
        """Test year validation."""
        gen = CrunchPasswordGenerator(2020, 2025)
        gen.validate_years()  # Should not raise
        
        gen.start_year = 2025
        gen.end_year = 2020
        with self.assertRaises(ValueError):
            gen.validate_years()
    
    def test_is_valid_date(self):
        """Test date validation."""
        gen = CrunchPasswordGenerator(2020, 2025)
        
        # Valid dates
        self.assertTrue(gen.is_valid_date(1, 1, 2020))
        self.assertTrue(gen.is_valid_date(29, 2, 2020))  # Leap year
        self.assertTrue(gen.is_valid_date(31, 12, 2020))
        
        # Invalid dates
        self.assertFalse(gen.is_valid_date(29, 2, 2021))  # Not leap year
        self.assertFalse(gen.is_valid_date(31, 4, 2020))  # April has 30 days
        self.assertFalse(gen.is_valid_date(32, 1, 2020))  # No 32nd day
        self.assertFalse(gen.is_valid_date(1, 13, 2020))  # No 13th month
    
    def test_count_valid_dates(self):
        """Test counting valid dates."""
        # 2020 is a leap year (366 days)
        gen_2020 = CrunchPasswordGenerator(2020, 2020)
        self.assertEqual(gen_2020.count_valid_dates(), 366)
        
        # 2021 is not a leap year (365 days)
        gen_2021 = CrunchPasswordGenerator(2021, 2021)
        self.assertEqual(gen_2021.count_valid_dates(), 365)
        
        # Two years
        gen_2020_2021 = CrunchPasswordGenerator(2020, 2021)
        self.assertEqual(gen_2020_2021.count_valid_dates(), 366 + 365)
    
    def test_get_file_size_estimate(self):
        """Test file size estimation."""
        gen = CrunchPasswordGenerator(2020, 2020)
        size = gen.get_file_size_estimate()
        
        # 366 dates * 9 bytes per line (8 chars + newline)
        expected_size = 366 * 9
        self.assertEqual(size, expected_size)
    
    def test_format_file_size(self):
        """Test file size formatting."""
        gen = CrunchPasswordGenerator(2020, 2020)
        
        self.assertEqual(gen.format_file_size(100), "100.0 B")
        self.assertEqual(gen.format_file_size(1024), "1.0 KB")
        self.assertEqual(gen.format_file_size(1048576), "1.0 MB")
        self.assertEqual(gen.format_file_size(1073741824), "1.0 GB")
    
    def test_generate_wordlist_with_crunch(self):
        """Test wordlist generation."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_path = f.name
        
        try:
            gen = CrunchPasswordGenerator(2023, 2023)
            result_path = gen.generate_wordlist_with_crunch(temp_path)
            
            self.assertEqual(result_path, temp_path)
            self.assertTrue(os.path.exists(temp_path))
            
            # Check file contents
            with open(temp_path, 'r') as f:
                lines = f.readlines()
            
            # Should have 365 lines (2023 is not a leap year)
            self.assertEqual(len(lines), 365)
            
            # Check first and last entries
            self.assertEqual(lines[0].strip(), "01012023")
            self.assertEqual(lines[-1].strip(), "31122023")
            
            # Check a few specific dates
            passwords = [line.strip() for line in lines]
            self.assertIn("01012023", passwords)  # New Year
            self.assertIn("25122023", passwords)  # Christmas
            self.assertNotIn("29022023", passwords)  # Invalid leap day
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestCrunchMultiFormatGenerator(unittest.TestCase):
    """Test the CrunchMultiFormatGenerator class."""
    
    def test_init_default_formats(self):
        """Test initialization with default formats."""
        gen = CrunchMultiFormatGenerator(2020, 2020)
        self.assertEqual(gen.formats, ['DDMMYYYY'])
    
    def test_init_custom_formats(self):
        """Test initialization with custom formats."""
        formats = ['DDMMYYYY', 'DDMMYY']
        gen = CrunchMultiFormatGenerator(2020, 2020, formats)
        self.assertEqual(gen.formats, formats)
    
    def test_validate_formats(self):
        """Test format validation."""
        # Valid formats
        gen = CrunchMultiFormatGenerator(2020, 2020, ['DDMMYYYY', 'DDMMYY'])
        gen.validate_formats()  # Should not raise
        
        # Invalid format
        with self.assertRaises(ValueError):
            CrunchMultiFormatGenerator(2020, 2020, ['INVALID'])
    
    def test_count_passwords_multiple_formats(self):
        """Test password counting with multiple formats."""
        gen = CrunchMultiFormatGenerator(2020, 2020, ['DDMMYYYY', 'DDMMYY'])
        count = gen.count_valid_dates() * len(gen.formats)
        
        # Should be 2 times the base count (366 * 2 for leap year 2020)
        expected = 366 * 2
        self.assertEqual(count, expected)
    
    def test_generate_format_wordlist(self):
        """Test format-specific wordlist generation."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_path = f.name
        
        try:
            gen = CrunchMultiFormatGenerator(2023, 2023, ['DDMMYY'])
            gen._generate_format_wordlist(temp_path, 'DDMMYY')
            
            self.assertTrue(os.path.exists(temp_path))
            
            with open(temp_path, 'r') as f:
                lines = f.readlines()
            
            # Check format - should be 6 characters (DDMMYY)
            first_password = lines[0].strip()
            self.assertEqual(len(first_password), 6)
            self.assertEqual(first_password, "010123")  # 01/01/23
            
            last_password = lines[-1].strip()
            self.assertEqual(last_password, "311223")  # 31/12/23
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestPasswordFormats(unittest.TestCase):
    """Test different password formats."""
    
    def test_ddmmyyyy_format(self):
        """Test DDMMYYYY format."""
        gen = CrunchMultiFormatGenerator(2020, 2020, ['DDMMYYYY'])
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_path = f.name
        
        try:
            gen._generate_format_wordlist(temp_path, 'DDMMYYYY')
            
            with open(temp_path, 'r') as f:
                first_line = f.readline().strip()
            
            self.assertEqual(first_line, "01012020")
            self.assertEqual(len(first_line), 8)
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_ddmmyy_format(self):
        """Test DDMMYY format."""
        gen = CrunchMultiFormatGenerator(2020, 2020, ['DDMMYY'])
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_path = f.name
        
        try:
            gen._generate_format_wordlist(temp_path, 'DDMMYY')
            
            with open(temp_path, 'r') as f:
                first_line = f.readline().strip()
            
            self.assertEqual(first_line, "010120")
            self.assertEqual(len(first_line), 6)
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_yyyymmdd_format(self):
        """Test YYYYMMDD format."""
        gen = CrunchMultiFormatGenerator(2020, 2020, ['YYYYMMDD'])
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_path = f.name
        
        try:
            gen._generate_format_wordlist(temp_path, 'YYYYMMDD')
            
            with open(temp_path, 'r') as f:
                first_line = f.readline().strip()
            
            self.assertEqual(first_line, "20200101")
            self.assertEqual(len(first_line), 8)
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main()