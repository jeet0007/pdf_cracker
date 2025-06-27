#!/usr/bin/env python3
"""
Tests for custom wordlist generators module.
"""

import tempfile
import os
import sys
from pathlib import Path
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.custom_wordlist_generators import CustomWordlistGenerator, DateWordlistGenerator


class TestDateWordlistGenerator:
    """Test the DateWordlistGenerator class."""
    
    @pytest.fixture
    def date_generator(self):
        """Create DateWordlistGenerator instance."""
        return DateWordlistGenerator()
    
    def test_generate_date_wordlist_ddmmyyyy(self, date_generator, temp_file):
        """Test date wordlist generation in DDMMYYYY format."""
        result = date_generator.generate_date_wordlist(
            temp_file, 2023, 2023, "DDMMYYYY"
        )
        
        assert result
        assert os.path.exists(temp_file)
        
        with open(temp_file, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 365  # 2023 is not a leap year
        assert lines[0].strip() == "01012023"
        assert lines[-1].strip() == "31122023"
    
    @pytest.mark.parametrize("date_format,expected_first,expected_length", [
        ("DDMMYY", "010123", 6),
        ("YYYYMMDD", "20230101", 8),
        ("DDMMYYYY", "01012023", 8),
    ])
    def test_date_formats(self, date_generator, temp_file, date_format, expected_first, expected_length):
        """Test different date formats."""
        result = date_generator.generate_date_wordlist(
            temp_file, 2023, 2023, date_format
        )
        
        assert result
        
        with open(temp_file, 'r') as f:
            first_line = f.readline().strip()
        
        assert len(first_line) == expected_length
        assert first_line == expected_first
    
    def test_generate_date_wordlist_invalid_format(self, date_generator, temp_file):
        """Test invalid date format."""
        result = date_generator.generate_date_wordlist(
            temp_file, 2023, 2023, "INVALID"
        )
        
        assert not result
    
    @pytest.mark.parametrize("year,expected_days", [
        (2020, 366),   # Leap year
        (2021, 365),   # Not leap year
        (2000, 366),   # Leap year (divisible by 400)
        (1900, 365),   # Not leap year (divisible by 100 but not 400)
    ])
    def test_leap_year_handling(self, date_generator, temp_file, year, expected_days):
        """Test proper leap year handling in date generation."""
        result = date_generator.generate_date_wordlist(temp_file, year, year, "DDMMYYYY")
        
        assert result
        
        with open(temp_file, 'r') as f:
            lines = f.readlines()
        
        # Just verify correct number of dates generated
        assert len(lines) == expected_days
        
        # Verify Feb 28 is always present
        feb28 = f"2802{year}"
        content = ''.join(lines)
        assert feb28 in content
    
    def test_generate_date_wordlist_with_progress(self, date_generator, temp_file):
        """Test date wordlist generation with progress callback."""
        progress_calls = []
        
        def progress_callback(progress, message):
            progress_calls.append((progress, message))
        
        result = date_generator.generate_date_wordlist(
            temp_file, 2023, 2023, "DDMMYYYY", progress_callback
        )
        
        assert result
        assert len(progress_calls) > 0
        
        # Check that we got start and end progress calls
        first_progress, first_message = progress_calls[0]
        last_progress, last_message = progress_calls[-1]
        
        assert first_progress == 0
        assert last_progress == 100
        assert "complete" in last_message.lower()
    
    def test_generate_buddhist_dates(self, date_generator, temp_file):
        """Test Buddhist calendar date generation."""
        result = date_generator.generate_buddhist_dates(
            temp_file, 2023, 2023, "DDMMYYYY"
        )
        
        assert result
        assert os.path.exists(temp_file)
        
        with open(temp_file, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 365  # 2023 is not a leap year
        # Buddhist year = Gregorian + 543, so 2023 -> 2566
        assert lines[0].strip() == "01012566"
        assert lines[-1].strip() == "31122566"
    
    @pytest.mark.parametrize("gregorian_year,buddhist_year", [
        (2023, 2566),
        (2020, 2563),
        (2000, 2543),
    ])
    def test_buddhist_year_conversion(self, date_generator, temp_file, gregorian_year, buddhist_year):
        """Test Buddhist year conversion (+543)."""
        result = date_generator.generate_buddhist_dates(
            temp_file, gregorian_year, gregorian_year, "DDMMYYYY"
        )
        
        assert result
        
        with open(temp_file, 'r') as f:
            first_line = f.readline().strip()
        
        expected_first = f"0101{buddhist_year}"
        assert first_line == expected_first
    
    def test_generate_buddhist_dates_with_progress(self, date_generator, temp_file):
        """Test Buddhist date generation with progress callback."""
        progress_calls = []
        
        def progress_callback(progress, message):
            progress_calls.append((progress, message))
        
        result = date_generator.generate_buddhist_dates(
            temp_file, 2023, 2023, "DDMMYYYY", progress_callback
        )
        
        assert result
        assert len(progress_calls) > 0
        
        # Check that we got proper progress calls
        last_progress, last_message = progress_calls[-1]
        assert last_progress == 100
        assert "complete" in last_message.lower()


class TestCustomWordlistGenerator:
    """Test the CustomWordlistGenerator class."""
    
    @pytest.fixture
    def custom_generator(self):
        """Create CustomWordlistGenerator instance."""
        return CustomWordlistGenerator()
    
    def test_generate_date_wordlist_delegation(self, custom_generator, temp_file):
        """Test that CustomWordlistGenerator properly delegates to DateWordlistGenerator."""
        result = custom_generator.generate_date_wordlist(
            temp_file, 2023, 2023, "DDMMYYYY"
        )
        
        assert result
        assert os.path.exists(temp_file)
        
        with open(temp_file, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 365
        assert lines[0].strip() == "01012023"
    
    def test_generate_buddhist_dates_delegation(self, custom_generator, temp_file):
        """Test that CustomWordlistGenerator properly delegates Buddhist date generation."""
        result = custom_generator.generate_buddhist_dates(
            temp_file, 2023, 2023, "DDMMYYYY"
        )
        
        assert result
        assert os.path.exists(temp_file)
        
        with open(temp_file, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 365
        assert lines[0].strip() == "01012566"  # 2023 + 543
    
    @pytest.mark.parametrize("start_year,end_year,expected", [
        (2020, 2020, 366),  # Leap year
        (2021, 2021, 365),  # Not leap year
        (2020, 2021, 366 + 365),  # Multiple years
    ])
    def test_calculate_date_count(self, custom_generator, start_year, end_year, expected):
        """Test date calculation function."""
        count = custom_generator.calculate_date_count(start_year, end_year)
        assert count == expected
    
    def test_date_generator_attribute(self, custom_generator):
        """Test that CustomWordlistGenerator has proper date_generator attribute."""
        assert hasattr(custom_generator, 'date_generator')
        assert isinstance(custom_generator.date_generator, DateWordlistGenerator)


class TestWordlistGeneratorIntegration:
    """Integration tests for wordlist generators."""
    
    def test_date_generator_standalone(self):
        """Test that DateWordlistGenerator can be used standalone."""
        generator = DateWordlistGenerator()
        assert generator is not None
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            result = generator.generate_date_wordlist(temp_path, 2023, 2023, "DDMMYYYY")
            assert result
            assert os.path.exists(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_custom_generator_composition(self):
        """Test that CustomWordlistGenerator properly composes DateWordlistGenerator."""
        custom_gen = CustomWordlistGenerator()
        date_gen = DateWordlistGenerator()
        
        # Both should provide the same interface
        assert hasattr(custom_gen, 'generate_date_wordlist')
        assert hasattr(custom_gen, 'generate_buddhist_dates')
        assert hasattr(custom_gen, 'calculate_date_count')
        
        assert hasattr(date_gen, 'generate_date_wordlist')
        assert hasattr(date_gen, 'generate_buddhist_dates')
    
    @pytest.mark.parametrize("years_back", [1, 5, 10])
    def test_multi_year_generation(self, years_back):
        """Test generation across multiple years."""
        from datetime import datetime
        
        generator = CustomWordlistGenerator()
        current_year = datetime.now().year
        start_year = current_year - years_back
        
        expected_count = generator.calculate_date_count(start_year, current_year)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            result = generator.generate_date_wordlist(temp_path, start_year, current_year, "DDMMYYYY")
            assert result
            
            with open(temp_path, 'r') as f:
                lines = f.readlines()
            
            assert len(lines) == expected_count
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


if __name__ == '__main__':
    pytest.main([__file__])