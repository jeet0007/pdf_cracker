#!/usr/bin/env python3
"""
Tests for wordlist generator CLI tools.
"""

import tempfile
import os
import sys
import subprocess
from pathlib import Path
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestWordlistGeneratorCLI:
    """Test the wordlist generator CLI tool."""
    
    @pytest.fixture
    def wordlist_gen_script(self):
        """Path to wordlist generator script."""
        return Path(__file__).parent.parent / 'src' / 'utils' / 'wordlist_gen.py'
    
    def test_help_option(self, wordlist_gen_script):
        """Test --help option."""
        result = subprocess.run([
            sys.executable, str(wordlist_gen_script), '--help'
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'Generate wordlists for date-based passwords' in result.stdout
        assert '--start' in result.stdout
        assert '--end' in result.stdout
    
    @pytest.mark.parametrize("year,expected_count", [
        (2023, "365"),  # Not leap year
        (2024, "366"),  # Leap year
    ])
    def test_estimate_only(self, wordlist_gen_script, year, expected_count):
        """Test --estimate-only option."""
        result = subprocess.run([
            sys.executable, str(wordlist_gen_script),
            '--start', str(year),
            '--end', str(year),
            '--estimate-only'
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert expected_count in result.stdout
        assert 'Estimate only' in result.stdout
    
    def test_invalid_year_range(self, wordlist_gen_script):
        """Test invalid year range."""
        result = subprocess.run([
            sys.executable, str(wordlist_gen_script),
            '--start', '2025',
            '--end', '2020',
            '--estimate-only'
        ], capture_output=True, text=True)
        
        assert result.returncode == 1
        assert 'Start year must be less than or equal to end year' in result.stderr
    
    @pytest.mark.slow
    def test_generate_small_wordlist(self, wordlist_gen_script, temp_file):
        """Test generating a small wordlist."""
        result = subprocess.run([
            sys.executable, str(wordlist_gen_script),
            '--start', '2023',
            '--end', '2023',
            '--output', temp_file
        ], capture_output=True, text=True, input='y\n', timeout=60)
        
        assert result.returncode == 0
        assert os.path.exists(temp_file)
        
        with open(temp_file, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 365  # 2023 is not a leap year
        assert lines[0].strip() == '01012023'
        assert lines[-1].strip() == '31122023'
    
    @pytest.mark.parametrize("date_format,expected_first,expected_length", [
        ("DDMMYY", "010123", 6),
        ("YYYYMMDD", "20230101", 8),
        ("DDMMYYYY", "01012023", 8),
    ])
    @pytest.mark.slow
    def test_date_formats(self, wordlist_gen_script, temp_file, date_format, expected_first, expected_length):
        """Test different date formats."""
        result = subprocess.run([
            sys.executable, str(wordlist_gen_script),
            '--start', '2023',
            '--end', '2023',
            '--format', date_format,
            '--output', temp_file
        ], capture_output=True, text=True, input='y\n', timeout=60)
        
        assert result.returncode == 0
        assert os.path.exists(temp_file)
        
        with open(temp_file, 'r') as f:
            first_line = f.readline().strip()
        
        assert len(first_line) == expected_length
        assert first_line == expected_first


class TestComprehensiveWordlistCLI:
    """Test the comprehensive wordlist generator CLI tool."""
    
    @pytest.fixture
    def comprehensive_gen_script(self):
        """Path to comprehensive wordlist generator script."""
        return Path(__file__).parent.parent / 'src' / 'utils' / 'comprehensive_wordlist.py'
    
    def test_help_option(self, comprehensive_gen_script):
        """Test --help option."""
        result = subprocess.run([
            sys.executable, str(comprehensive_gen_script), '--help'
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'Generate comprehensive PDF password wordlist' in result.stdout
        assert '--years-back' in result.stdout
        assert '--estimate-only' in result.stdout
    
    def test_estimate_only(self, comprehensive_gen_script):
        """Test --estimate-only option."""
        result = subprocess.run([
            sys.executable, str(comprehensive_gen_script),
            '--years-back', '1',  # Small range for testing
            '--estimate-only'
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'Gregorian dates:' in result.stdout
        assert 'Buddhist dates:' in result.stdout
        assert '8-digit numbers:' in result.stdout
        assert '100,000,000' in result.stdout  # 8-digit numbers count
        assert 'Estimate complete' in result.stdout
    
    @pytest.mark.parametrize("years_back", [1, 5, 10])
    def test_estimate_different_years_back(self, comprehensive_gen_script, years_back):
        """Test estimation with different years back."""
        result = subprocess.run([
            sys.executable, str(comprehensive_gen_script),
            '--years-back', str(years_back),
            '--estimate-only'
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'Total passwords:' in result.stdout


class TestWordlistGeneratorIntegration:
    """Integration tests for wordlist generator."""
    
    def test_import_wordlist_gen_module(self):
        """Test importing the wordlist generator module."""
        try:
            import utils.wordlist_gen as wordlist_gen
            assert hasattr(wordlist_gen, 'main')
        except ImportError as e:
            pytest.fail(f"Failed to import wordlist_gen: {e}")
    
    def test_import_comprehensive_wordlist_module(self):
        """Test importing the comprehensive wordlist generator module."""
        try:
            import utils.comprehensive_wordlist as comprehensive_wordlist
            assert hasattr(comprehensive_wordlist, 'main')
        except ImportError as e:
            pytest.fail(f"Failed to import comprehensive_wordlist: {e}")
    
    def test_crunch_wrapper_integration(self):
        """Test integration with CrunchWrapper."""
        from core.crunch_wrapper import CrunchWrapper
        
        crunch = CrunchWrapper()
        assert crunch is not None
        assert crunch.has_crunch in [True, False]
    
    @pytest.mark.parametrize("start_year,end_year,expected", [
        (2020, 2020, 366),  # Leap year
        (2021, 2021, 365),  # Not leap year
        (2020, 2021, 366 + 365),  # Multiple years
    ])
    def test_date_calculation_function(self, start_year, end_year, expected):
        """Test date calculation function."""
        from utils.wordlist_gen import calculate_date_count
        
        count = calculate_date_count(start_year, end_year)
        assert count == expected
    
    def test_comprehensive_stats_calculation(self):
        """Test comprehensive wordlist statistics calculation."""
        from utils.comprehensive_wordlist import calculate_comprehensive_stats
        
        stats = calculate_comprehensive_stats(1)  # 1 year back
        
        assert 'gregorian_dates' in stats
        assert 'buddhist_dates' in stats
        assert 'numbers' in stats
        assert 'total_passwords' in stats
        assert 'file_size_mb' in stats
        
        # Buddhist and Gregorian should have same count
        assert stats['gregorian_dates'] == stats['buddhist_dates']
        
        # Numbers should be 100 million
        assert stats['numbers'] == 100000000
        
        # Total should be sum of all parts
        expected_total = stats['gregorian_dates'] + stats['buddhist_dates'] + stats['numbers']
        assert stats['total_passwords'] == expected_total