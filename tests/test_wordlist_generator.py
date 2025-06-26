#!/usr/bin/env python3
"""
Tests for wordlist generator CLI.
"""

import unittest
import tempfile
import os
import sys
import subprocess
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestWordlistGeneratorCLI(unittest.TestCase):
    """Test the wordlist generator CLI tool."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.src_dir = Path(__file__).parent.parent / 'src'
        self.wordlist_gen = self.src_dir / 'wordlist_gen.py'
    
    def test_help_option(self):
        """Test --help option."""
        result = subprocess.run([
            sys.executable, str(self.wordlist_gen), '--help'
        ], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0)
        self.assertIn('Generate wordlists for date-based passwords', result.stdout)
        self.assertIn('--start', result.stdout)
        self.assertIn('--end', result.stdout)
    
    def test_estimate_only(self):
        """Test --estimate-only option."""
        result = subprocess.run([
            sys.executable, str(self.wordlist_gen),
            '--start', '2023',
            '--end', '2023',
            '--estimate-only'
        ], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0)
        self.assertIn('365 passwords', result.stdout)  # 2023 is not a leap year
        self.assertIn('Estimate only', result.stdout)
    
    def test_estimate_leap_year(self):
        """Test estimation for leap year."""
        result = subprocess.run([
            sys.executable, str(self.wordlist_gen),
            '--start', '2024',
            '--end', '2024',
            '--estimate-only'
        ], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0)
        self.assertIn('366 passwords', result.stdout)  # 2024 is a leap year
    
    def test_invalid_year_range(self):
        """Test invalid year range."""
        result = subprocess.run([
            sys.executable, str(self.wordlist_gen),
            '--start', '2025',
            '--end', '2020',
            '--estimate-only'
        ], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 1)
        self.assertIn('Start year must be less than or equal to end year', result.stderr)
    
    def test_generate_small_wordlist(self):
        """Test generating a small wordlist."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            temp_path = f.name
        
        try:
            result = subprocess.run([
                sys.executable, str(self.wordlist_gen),
                '--start', '2023',
                '--end', '2023',
                '--output', temp_path
            ], capture_output=True, text=True, input='y\n')  # Auto-confirm overwrite
            
            self.assertEqual(result.returncode, 0)
            self.assertTrue(os.path.exists(temp_path))
            
            # Check file contents
            with open(temp_path, 'r') as f:
                lines = f.readlines()
            
            self.assertEqual(len(lines), 365)  # 2023 is not a leap year
            self.assertEqual(lines[0].strip(), '01012023')
            self.assertEqual(lines[-1].strip(), '31122023')
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_verbose_output(self):
        """Test verbose output option."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            temp_path = f.name
        
        try:
            result = subprocess.run([
                sys.executable, str(self.wordlist_gen),
                '--start', '2023',
                '--end', '2023',
                '--output', temp_path,
                '--verbose'
            ], capture_output=True, text=True, timeout=30)
            
            self.assertEqual(result.returncode, 0)
            # Verbose mode should show some progress information
            # (May or may not show progress bars depending on timing)
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_multiple_formats(self):
        """Test multiple format generation."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            temp_path = f.name
        
        try:
            result = subprocess.run([
                sys.executable, str(self.wordlist_gen),
                '--start', '2023',
                '--end', '2023',
                '--output', temp_path,
                '--formats', 'DDMMYYYY', 'DDMMYY'
            ], capture_output=True, text=True)
            
            self.assertEqual(result.returncode, 0)
            self.assertTrue(os.path.exists(temp_path))
            
            # Check file contents - should have both formats
            with open(temp_path, 'r') as f:
                lines = f.readlines()
            
            # Should have 365 * 2 = 730 lines
            self.assertEqual(len(lines), 730)
            
            passwords = [line.strip() for line in lines]
            
            # Check for both formats
            self.assertIn('01012023', passwords)  # DDMMYYYY
            self.assertIn('010123', passwords)    # DDMMYY
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestWordlistGeneratorIntegration(unittest.TestCase):
    """Integration tests for wordlist generator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.src_dir = Path(__file__).parent.parent / 'src'
        sys.path.insert(0, str(self.src_dir))
    
    def test_import_wordlist_gen_module(self):
        """Test importing the wordlist generator module."""
        try:
            import wordlist_gen
            self.assertTrue(hasattr(wordlist_gen, 'main'))
        except ImportError as e:
            self.fail(f"Failed to import wordlist_gen: {e}")
    
    def test_password_generator_integration(self):
        """Test integration with password generator."""
        from core.password_generator import CrunchPasswordGenerator
        
        gen = CrunchPasswordGenerator(2023, 2023)
        count = gen.count_valid_dates()
        self.assertEqual(count, 365)
        
        # Test file size estimation
        size = gen.get_file_size_estimate()
        expected_size = 365 * 9  # 8 chars + newline
        self.assertEqual(size, expected_size)
    
    def test_date_validation_edge_cases(self):
        """Test date validation edge cases."""
        from core.password_generator import CrunchPasswordGenerator
        
        gen = CrunchPasswordGenerator(2000, 2000)  # Leap year (divisible by 400)
        self.assertTrue(gen.is_valid_date(29, 2, 2000))
        
        gen = CrunchPasswordGenerator(1900, 1900)  # Not leap year (divisible by 100 but not 400)
        self.assertFalse(gen.is_valid_date(29, 2, 1900))
        
        gen = CrunchPasswordGenerator(2004, 2004)  # Leap year (divisible by 4)
        self.assertTrue(gen.is_valid_date(29, 2, 2004))
        
        gen = CrunchPasswordGenerator(2001, 2001)  # Not leap year
        self.assertFalse(gen.is_valid_date(29, 2, 2001))


if __name__ == '__main__':
    unittest.main()